from datetime import datetime
from airflow.models.baseoperator import BaseOperator
from torch_airflow_sdk.utils.torch_client import TorchDAGClient
from urllib import parse
from torch_sdk.events.generic_event import GenericEvent


class TorchInitializer(BaseOperator):
    """
    In airflow 2.0 , you need to add task with given operator at the root of your dag. This will create new pipeline
    run for your dag run. In airflow 1.0, its not needed. We've taken care inside our code. But for 2.0, you need to
    add it as a root of the dag. This is because of DAG serialization in version 2.0. So, to fulfill that requirement
    we need add additional operator for 2.0.

    You need to add extra parameter pipeline uid. Other parameters will be same as std airflow base operator's parameters

    """

    def __init__(self, *, pipeline_uid, **kwargs):
        """
        You need to add extra parameter pipeline uid. Other parameters will be same as std airflow base operator's parameters
        :param pipeline_uid: uid of the pipeline
        """
        super().__init__(**kwargs)
        self.pipeline_uid = pipeline_uid

    def execute(self, context):
        client = TorchDAGClient()
        pipeline_res = client.get_pipeline(self.pipeline_uid)
        pipeline_run = pipeline_res.create_pipeline_run()
        # pipeline_run.create_span(uid=f'{self.pipeline_uid}.span', context_data={'time': str(datetime.now())})
        parent_span_context = pipeline_run.create_span(uid=f'{self.pipeline_uid}.span')
        try:
            log_url = list({context.get('task_instance').log_url})
            list_ = list(log_url)
            url = list_[0]
            parsed = parse.urlsplit(url)
            query = parse.parse_qs(parse.urlsplit(url).query)
            dag_id = query['dag_id'][0]
            execution_date = query['execution_date'][0]
            encoded_time = parse.quote(execution_date)
            dagrun_url = parsed.scheme + '://' + parsed.netloc + '/graph?root=&dag_id=' + dag_id + '&execution_date=' + encoded_time + '&arrang=LR'
            parent_span_context.send_event(GenericEvent(
                context_data={
                    'dag_id': dag_id,
                    'time': str(datetime.now()),
                    'url': dagrun_url,
                    'execution_time': execution_date
                },
                event_uid='AIRFLOW.DETAILS')
            )
        except:
            pass
