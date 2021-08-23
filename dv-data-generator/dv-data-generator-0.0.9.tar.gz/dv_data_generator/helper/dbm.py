import time


def get_report_url(service, query_id, sleep_limit=60):
    result = None
    exponantial_sleep = 1
    while not result:
        time.sleep(exponantial_sleep)
        try:
            query = service.queries().getquery(queryId=query_id).execute()
            result = query if not query["metadata"]["running"] else None
        except Exception as e:
            if exponantial_sleep >= sleep_limit:
                raise e
        exponantial_sleep += 1
    return result["metadata"]["googleCloudStoragePathForLatestReport"]


def try_run(method, value, fail_method=None, sleep_limit=10):
    exponantial_sleep = 1
    failed = True
    data = {}
    while failed:
        time.sleep(exponantial_sleep)
        try:
            data = method(value)
            failed = False
        except Exception as err:
            if fail_method:
                return fail_method(value)
            if exponantial_sleep >= sleep_limit:
                raise err
        exponantial_sleep += 1
    return data
