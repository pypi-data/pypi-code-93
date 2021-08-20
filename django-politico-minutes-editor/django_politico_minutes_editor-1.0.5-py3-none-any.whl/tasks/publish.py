import logging

from celery import shared_task
from django.conf import settings
from minutes.models import Edition
from minutes.utils.aws_lambda import invoke

headers = {
    "Authorization": "Token {}".format(settings.MINUTES_API_TOKEN),
    "Content-Type": "application/json",
}

logger = logging.getLogger("django")


@shared_task(acks_late=True)
def publish(epk, mode="STAGING"):
    edition = Edition.objects.get(id=epk)
    vertical = edition.vertical.slug

    data = {
      "body": {
        "manual": True,
        "testing": settings.DEBUG,
        "token": settings.MINUTES_BAKERY_TOKEN,
        "mode": mode,
        "verticalSlug": vertical,
        "editionId": str(edition.id)
      }
    }

    resp = invoke(data)

    if mode == "PRODUCTION" and resp.ok:
        e = Edition.objects.get(id=edition)
        e.is_published = True
        e.save()

    return resp


@shared_task(acks_late=True)
def unpublish(edition):
    pass
    # data = {"action": "unpublish", "data": edition}
    #
    # e = Edition.objects.get(id=edition)
    # e.live = False
    # e.save()
    #
    # if e == Edition.objects.latest_live(e.vertical):
    #     publish_latest(e.vertical.id.hex)
    #
    # requests.post(settings.MINUTES_BAKERY_URL, json=data, headers=headers)


@shared_task(acks_late=True)
def publish_latest(vertical):
    # change this to PRODUCTION when launching
    e = Edition.objects.latest_live(vertical)
    publish(str(e.id), "PRODUCTION")


@shared_task(acks_late=True)
def publish_if_ready(edition):
    e = Edition.objects.get(id=edition)
    if e.should_publish():
        # change this to PRODUCTION when launching
        publish(edition, "PRODUCTION")


@shared_task(acks_late=True)
def autopublisher():
    logger.info("MINUTES: Starting autopublishing cycle...")
    for e in Edition.objects.all():
        logger.info('MINUTES: Publishing edition "{}" if ready...'.format(
            e.id
        ))
        publish_if_ready(e.id)
    logger.info("MINUTES: Autopublishing cycle complete.")
