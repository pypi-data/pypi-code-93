import blaster
from blaster import config
import time
from blaster.aws.push_tasks import run_later
from blaster.urllib_utils import get_data

from blaster.aws.push_tasks import start_boto_sqs_readers, wait_for_push_tasks_processing


blaster.config.aws_config = {
	'aws_access_key_id': "AKIAIBWZGQON6WDWEWMA",
	'aws_secret_access_key': "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",
	'region_name': "ap-south-1"
}
blaster.config.sqs_url = "https://sqs.ap-south-1.amazonaws.com/835285030471/crawl-readings"


@run_later
def crawl_this(url, param1="hello", param2="hello"):
	print("reading url", url, get_data(url).read()[:100])
	time.sleep(5)

@run_later
def crawl_with_exception(url, param1=None, param2=None):
	print("Throwing exception :", url, param1, param2)
	raise Exception()


# 5 threads
start_boto_sqs_readers()

#commands/run later functions
crawl_this("https://google.com")
crawl_with_exception("https://google.com")

# until you call blaster.base.stop_all_apps() or SIGKILL,
# so basically runs indefinitely
wait_for_push_tasks_processing()
