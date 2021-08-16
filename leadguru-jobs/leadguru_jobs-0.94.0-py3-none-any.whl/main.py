import json
import sys
import threading
import time
from lgt_jobs import BackgroundJobRunner, jobs_map
from lgt.common.python.pubsub.pubsubfactory import PubSubFactory
from lgt.common.python.lgt_logging import log
from prometheus_client import Histogram, CollectorRegistry, push_to_gateway

from lgt_jobs import env

lock = threading.Lock()

metric_registry = CollectorRegistry()
metric_histogram = Histogram("bg_job_processing_time", "Time spent processing background job", labelnames=["job_type", "env", "status"],
                            registry=metric_registry)

def run_background_job(data):
    job_type = data["job_type"]
    start = time.time()
    try:
        log.info(f"[JOB]: {data} [START]")

        BackgroundJobRunner.run(jobs_map=jobs_map, data=data)
        total = time.time() - start
        metric_histogram.labels(job_type, env.environment, "success").observe(total.real)
        log.info(f"[JOB]: {data} [FINISHED]")
    except Exception:
        total = time.time() - start
        metric_histogram.labels(job_type, env.environment, "error").observe(total.real)
        raise
    finally:
        push_to_gateway(env.push_gateway_url, job="bg_job", registry=metric_registry)

def run_background_job_with_lock(message):
    try:
        data = json.loads(message.data)
        with lock:
            run_background_job(data)
    except:
        import traceback
        log.error(f"[ERROR][JOB]: {message.data} [ERROR] {traceback.format_exception(*sys.exc_info())} ")
        traceback.print_exception(*sys.exc_info())
    finally:
        # accept message any way
        message.ack()


if __name__ == '__main__':
    factory = PubSubFactory(env.project_id)
    factory.create_topic_if_doesnt_exist(env.background_jobs_topic)
    factory.create_subscription_if_doesnt_exist(env.background_jobs_subscriber, env.background_jobs_topic, ack_deadline_seconds=600)
    bot_subscription_path = factory.get_subscription_path(env.background_jobs_subscriber, env.background_jobs_topic)

    factory.subscriber.subscribe(bot_subscription_path, callback=run_background_job_with_lock)
    print(f'Listening for messages on {bot_subscription_path}')
    while True:
        time.sleep(1)