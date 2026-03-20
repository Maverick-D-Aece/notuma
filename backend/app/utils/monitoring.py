import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def setup_monitoring():
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
        )
        print("Sentry monitoring initialized.")
    else:
        print("SENTRY_DSN not set. Monitoring disabled.")
