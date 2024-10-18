import requests
from pydantic import BaseModel
import os
import xml.etree.ElementTree as ET
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Article, Sitemap, SystemPromptModel
from openai import OpenAI


def generate_system_prompt(keywords, internal_linking):
    """
    Generate a system prompt for the AI to refactor the article based on a keyword.

    :param keyword: The keyword to optimize the article for
    :return: The system prompt
    """
    return SystemPromptModel(keywords=keywords, internal_linking=internal_linking)


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
    structure: BaseModel, system_prompt: SystemPromptModel, user_message: str
):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt.generate_prompt()},
            {"role": "user", "content": user_message},
        ],
        response_format=structure,
    )
    return completion.choices[0].message.parsed


class SuggestionsList(BaseModel):
    suggested_keyword: str
    suggestions: list[SuggestionModel]


def suggest_changes_to_article(article_id: int):
    from .tasks import suggest_changes_to_article_task  # Importar aquí para evitar la importación circular
    suggest_changes_to_article_task.delay(article_id)
