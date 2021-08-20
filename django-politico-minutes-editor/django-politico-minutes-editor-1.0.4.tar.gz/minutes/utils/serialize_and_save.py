import logging

logger = logging.getLogger("api")


def serialize_and_save(serializer):
    if not serializer.is_valid():
        logger.error(serializer.errors)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
