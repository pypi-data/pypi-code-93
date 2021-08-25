# Time in minutes before a Compute Node always shuts down
COMPUTE_NODE_AUTO_SHUTDOWN_TIME_MINUTES = 1440  # 24 hours

# Time in minutes before a Compute Node running a job shuts down
COMPUTE_NODE_RUNNING_JOB_SHUTDOWN_TIME_MINUTES = 30

LOG_FILE_PATH = '/tmp/biolib.log'

GUNICORN_REQUEST_TIMEOUT = 300

VSOCK_PROXY_PATH = '/home/ec2-user/biolib-nitro-enclave-ami-setup/biolib-vsock-proxy'

DEFAULT_PORT = '5000'
