from saleboxdjango.models import SyncLog


def log(function_name, message, status='INFO'):
    SyncLog(
        status=status,
        function_name=function_name,
        message=message
    ).save()

    # admin emails
    if status == 'ERROR':
        # send email here...
        pass