from .tasks import suggest_changes_to_article_task

def suggest_changes_to_article(article_id: int):
    suggest_changes_to_article_task.delay(article_id)