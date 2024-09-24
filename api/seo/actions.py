import requests
from pydantic import BaseModel
import os
import xml.etree.ElementTree as ET
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Article, Sitemap, Suggestion
from openai import OpenAI


def generate_system_prompt(keywords, internal_linking):
    """
    Generate a system prompt for the AI to refactor the article based on a keyword.

    :param keyword: The keyword to optimize the article for
    :return: The system prompt
    """
    return f"""
You are a SEO specialist. 
Refactor the following article to optimize the internal linking of it.
The keywords of the article is: {keywords}
Note: If there are a empty list of keywords, please suggest at least 3.

Please write the SuggestionsList like a SEO expert with more than 40 years of experience. The goal is to IMPROVE parts of the article. You must identify areas where an internal linking may be beneficial using the provided links down below. The internal linking should be made properly following SEO tips.

For example: 
original_text: "To create an AI application we must think about the features we want to add"
replacement_text: "T0 [create an AI application](link for some related article that talks about this topic) we must think about the features we want to add"

Also, if you identify that the content of the article may be extended in some part, feel free to add it!

You have all free creative thinking.

---LINKS YOU MAY USE FOR INTERNAL LINKING
{internal_linking}
---

The task is to REWRITE parts of the article to improve **internal linking**.

- Suggest at least 20 changes that can be made to the article.
- Keep in mind this about each suggestion: 
The `original_text` must be an exact match of the part of the article where an internal link can be added. Keep in mind that this text must have at least 5 words in order to avoid problems when replacing the content with the suggested one.

- 

The `replacement_text` must replace the original_text adding internal links or improving misspelings, fixing things...

- You can also suggest new article to create them if you think is necessary. To do so, when adding the link so it like: [NEW: text of the link](possible article link)

- Think about missing topics in the article based in the provided search results article that can be added to the content.


    """


def fetch_sitemap_urls(sitemap_url):
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


def get_all_urls_from_sitemap(sitemap_index_url):
    sitemap_urls = fetch_main_sitemap(sitemap_index_url)

    # Exclude specific sitemap URLs
    exclude_urls = [
        "https://4geeks.com/pages-sitemap.xml",
        "https://4geeks.com/technologies-sitemap.xml",
    ]
    sitemap_urls = [url for url in sitemap_urls if url not in exclude_urls]

    all_urls = []
    for sitemap_url in sitemap_urls:
        urls = fetch_sitemap_urls(sitemap_url)
        all_urls.extend(urls)

    # slugs = [get_last_part_of_url(url) for url in all_urls]

    return all_urls


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


def create_article_from_json(sitemap: Sitemap, json_data):
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
        max_tokens=500,
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
        model="gpt-4o-2024-08-06",
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

    a = Article.objects.get(pk=article_id)
    all_articles_with_the_same_language = Article.objects.filter(language=a.language)
    articles_links = "\n".join(
        [f"{a.title}: {a.url}" for a in all_articles_with_the_same_language]
    )

    system_prompt = generate_system_prompt(a.keywords, articles_links)

    article_text = f"{a.content}"

    suggestions_list: SuggestionsList = create_structured_completion(
        SuggestionsList, system_prompt, article_text
    )
    for s in suggestions_list.suggestions:
        Suggestion.objects.create(
            original_text=s.original_text,
            replacement_text=s.replacement_text,
            article=a,
        )

    return suggestions_list
