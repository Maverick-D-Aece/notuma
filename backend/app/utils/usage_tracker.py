from sqlalchemy.orm import Session
from backend.app.models import UsageLog
from typing import Optional, Dict, Any

def log_usage(
    db: Session,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    service: str = "image_generation",
    provider: Optional[str] = None,
    metric: str = "images",
    amount: int = 1,
    cost_metadata: Optional[Dict[str, Any]] = None
):
    try:
        new_log = UsageLog(
            user_id=user_id,
            project_id=project_id,
            service=service,
            provider=provider,
            metric=metric,
            amount=amount,
            cost=cost_metadata
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        # In a real scenario, we might want to log this error to Sentry,
        # but don't want to fail the main request because usage logging failed.
        print(f"Error logging usage: {e}")
        db.rollback()
