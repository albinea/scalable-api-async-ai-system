from celery import shared_task

from .agent import run_agent


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def run_ai_inference(self, session_id, user_message):

    result = run_agent(
        session_id=session_id,
        user_message=user_message,
    )

    return {
        "session_id": session_id,
        "response": result,
    }