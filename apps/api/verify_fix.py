
import sys
import os
import asyncio

# Setup path
sys.path.append(os.getcwd())

from app.core.config import get_settings
from app.core.celery_utils import enqueue_interview_processing
from app.models.enums import JobStatus
from app.core.celery_utils import enqueue_interview_processing
from app.models.enums import JobStatus

# We need to mock session or use real one
# Let's just check the Redis URL first

def verify_redis_config():
    print("--- Verifying Redis Config ---")
    settings = get_settings()
    url = settings.get_redis_url()
    print(f"Redis URL from settings: {url}")
    
    if "ssl_cert_reqs=CERT_NONE" in url:
        print("SUCCESS: SSL param is present.")
    else:
        print("FAILURE: SSL param is MISSING.")
        
    # Check Celery App config
    from app.core.celery_utils import celery_app
    print(f"Celery Broker URL: {celery_app.conf.broker_url}")
    
    if "ssl_cert_reqs=CERT_NONE" in celery_app.conf.broker_url:
        print("SUCCESS: Celery Broker URL has SSL param.")
    else:
         print("FAILURE: Celery Broker URL matches settings? " + str(celery_app.conf.broker_url == url))

def try_send_task():
    print("\n--- Verifying Task Sending ---")
    from app.core.celery_utils import celery_app
    try:
        with celery_app.connection() as connection:
            connection.ensure_connection(max_retries=1)
            print("Connection verified.")
            
        task = celery_app.send_task("vibecheck.tasks.process_interview", args=["test-job-id"])
        print(f"Task sent successfully. ID: {task.id}")
    except Exception as e:
        print(f"Failed to send task: {e}")

if __name__ == "__main__":
    verify_redis_config()
    try_send_task()
