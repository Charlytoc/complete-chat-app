from .models import Article, Suggestion
from .actions import generate_system_prompt, create_structured_completion, SuggestionsList

def suggest_changes_to_article_logic(article_id: int):
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

    return True