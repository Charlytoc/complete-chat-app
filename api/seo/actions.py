import requests
from pydantic import BaseModel
import os
import xml.etree.ElementTree as ET

# from django.utils import timezone
# from django.contrib.auth.models import User
from .models import Article, SitemapIndex, SystemPromptModel, Sitemap, Suggestion
from openai import OpenAI
import re
from urllib.parse import urlparse
import random

WORDS = [
    "lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "curabitur",
    "vel",
    "viverra",
    "nunc",
    "eu",
    "nisl",
    "auctor",
    "volutpat",
    "sapien",
    "vulputate",
    "mauris",
    "pellentesque",
    "porta",
    "nisi",
    "vitae",
    "mollis",
    "nunc",
    "euismod",
    "diam",
    "nec",
    "sem",
    "nulla",
    "sagittis",
    "sodales",
    "tincidunt",
    "maecenas",
    "suscipit",
]


def generate_random_words():
    """
    return three random words
    """
    return " ".join([random.choice(WORDS) for i in range(3)])


def generate_prompt(links):
    return f"""
You are a SEO specialist. 
Refactor the following article to optimize the internal linking of it.

Please write the SuggestionsList like a SEO expert with more than 40 years of experience. The goal is to IMPROVE parts of the article. You must identify areas where an internal linking may be beneficial using the provided links down below. The internal linking should be made properly following SEO tips.

For example: 
original_text: "To create an AI application we must think about the features we want to add"
replacement_text: "To [create an AI application](link for some related article that talks about this topic) we must think about the features we want to add"

Also, if you identify that the content of the article may be extended in some part, feel free to add it!

You have all free creative thinking.

---LINKS YOU CAN USE FOR INTERNAL LINKING
{links}
---

The task is to REWRITE parts of the article to improve **internal linking**.

- Suggest at least 20 changes that can be made to the article.
- Keep in mind this about each suggestion: 
The `original_text` must be an exact match of the part of the article where an internal link can be added. Keep in mind that this text must have at least 5 words in order to avoid problems when replacing the content with the suggested one.

The `replacement_text` must replace the original_text adding internal links or improving misspellings, fixing things...

- You can also suggest new articles to create them if you think is necessary. To do so, when adding the link so it like: [NEW: text of the link](possible article link)

- Think about missing topics in the article based on the provided search results article that can be added to the content.
        """


def generate_system_prompt(keywords, internal_linking):
    """
    Generate a system prompt for the AI to refactor the article based on a keyword.

    :param keyword: The keyword to optimize the article for
    :return: The system prompt
    """
    return SystemPromptModel(keywords=keywords, internal_linking=internal_linking)


def fetch_sitemap_urls(sitemap_url):
    print(sitemap_url)
    if not isinstance(sitemap_url, str):
        return []

    # Validate if the URL is a sitemap
    if not sitemap_url.endswith(".xml"):
        return []
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)
    namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        url.find("ns:loc", namespaces).text
        for url in root.findall("ns:url", namespaces)
    ]
    return urls


def fetch_main_sitemap(sitemap_index_url):
    response = requests.get(sitemap_index_url)
    root = ET.fromstring(response.content)

    namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [
        sitemap.find("ns:loc", namespaces).text
        for sitemap in root.findall("ns:sitemap", namespaces)
    ]
    return sitemap_urls


# def get_all_urls_from_sitemap(sitemap_index_url):
#     sitemap_urls = fetch_main_sitemap(sitemap_index_url)
#     # return sitemap_urls
#     # Exclude specific sitemap URLs
#     exclude_urls = [
#         "https://4geeks.com/pages-sitemap.xml",
#         "https://4geeks.com/technologies-sitemap.xml",
#     ]
#     sitemap_urls = [url for url in sitemap_urls if url not in exclude_urls]

#     all_urls = []
#     for sitemap_url in sitemap_urls:
#         urls = fetch_sitemap_urls(sitemap_url)
#         all_urls.extend(urls)

#     return all_urls


def sanitize_url_to_title(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)

    # Get the path and remove leading/trailing slashes
    path = parsed_url.path.strip("/")

    # Remove any query parameters or fragments
    # This keeps only the path portion of the URL
    title = path.split("?")[0].split("#")[0]

    # Replace slashes with spaces or hyphens
    title = re.sub(r"/", " ", title)  # Replace slashes with spaces
    title = re.sub(r"[-_]", " ", title)  # Replace hyphens and underscores with spaces

    # Remove any extra whitespace
    title = re.sub(r"\s+", " ", title).strip()

    # If the title is empty after sanitization, fall back to a default string
    if not title:
        title = "Untitled Article"

    return title


def get_all_sitemap_urls_for_index(sitemap_index_url):
    sitemap_urls = fetch_main_sitemap(sitemap_index_url)
    return sitemap_urls


def get_all_urls_for_a_sitemap(sitemap_id: int):
    s = Sitemap.objects.get(id=sitemap_id)
    urls = fetch_sitemap_urls(s.url)
    articles_to_create = []

    for url in urls:
        if not Article.objects.filter(url=url, sitemap=s).exists():
            articles_to_create.append(
                Article(sitemap=s, url=url, title=sanitize_url_to_title(url))
            )

    Article.objects.bulk_create(articles_to_create)

    return urls


def get_last_part_of_url(url):
    return url.rstrip("/").split("/")[-1]


def fetch_asset_data(slug):
    url = f"https://breathecode.herokuapp.com/v1/registry/asset/{slug}"
    response = requests.get(url)
    return response.json()


def fetch_raw_github_content(readme_url):
    # Convert the GitHub URL to the raw content URL
    raw_url = readme_url.replace("github.com", "raw.githubusercontent.com").replace(
        "/blob/", "/"
    )

    # Fetch the raw content
    response = requests.get(raw_url)

    # Check if the request was successful
    if response.status_code == 200:
        return response.text
    else:
        return None


def create_article_from_json(sitemap: SitemapIndex, json_data):
    readme_url = json_data.get("readme_url", None)
    content = fetch_raw_github_content(readme_url)

    article, created = Article.objects.get_or_create(
        slug=json_data["slug"],
        defaults={
            "sitemap": sitemap,
            "content": content,
            "title": json_data.get("title", ""),
            "keywords": json_data.get("seo_keywords", []),
            "language": json_data.get("lang", "en"),
            "url": json_data.get("url", None),
            "description": json_data.get("description", ""),
            # TODO: ADd the academy property when creating the articles
            "academy_id": json_data.get("academy_id", None),
        },
    )
    return article


def create_completion_openai(
    system_prompt: str, user_message: str, model="gpt-4o-mini"
):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    completion = client.chat.completions.create(
        model=model,
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content


class SuggestionModel(BaseModel):
    original_text: str
    replacement_text: str


def create_structured_completion(
    structure: BaseModel, system_prompt: str, user_message: str
):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format=structure,
    )
    return completion.choices[0].message.parsed


class SuggestionsList(BaseModel):
    suggested_keyword: str
    suggestions: list[SuggestionModel]


def suggest_changes_to_article(article_id: int):
    from .tasks import (
        suggest_changes_to_article_task,
    )

    suggest_changes_to_article_task.delay(article_id)


# def get_sitemap_index(domain: str):
#     if domain.endswith(".xml"):
#         return domain
#     return f"https://{domain}/sitemap_index.xml"


def get_all_sitemaps(sitemap_index_id: int):
    try:
        sitemap_index = SitemapIndex.objects.get(id=sitemap_index_id)
        urls = get_all_sitemap_urls_for_index(sitemap_index.url)
        for url in urls:
            if url.endswith(".xml"):
                try:
                    s = Sitemap.objects.get(index=sitemap_index, url=url)
                except Sitemap.DoesNotExist:
                    s = Sitemap(index=sitemap_index, url=url)
                    s.save()
        return True
    except Exception as e:
        print(e)
        return False

        # async_fetch_article.delay(domain, url)


def suggest_internal_linking(article_id: int):
    a = Article.objects.get(pk=article_id)
    all_sitemap_articles = Article.objects.filter(sitemap__index=a.sitemap.index)
    articles_links = "\n".join([f"{a.title}: {a.url}" for a in all_sitemap_articles])

    system_prompt = generate_prompt(articles_links)
    article_text = f"{a.article_content_md}"

    suggestions_list: SuggestionsList = create_structured_completion(
        SuggestionsList, system_prompt, article_text
    )

    for s in suggestions_list.suggestions:
        Suggestion.objects.create(
            original_text=s.original_text,
            replacement_text=s.replacement_text,
            article=a,
        )

    return True
