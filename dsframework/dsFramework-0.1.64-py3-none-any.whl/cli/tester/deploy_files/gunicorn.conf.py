import multiprocessing
bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 60 # Workers silent for more than this many seconds are killed and restarted
graceful_timeout = 60 # After receiving a restart signal, workers have this much time to finish serving requests
worker_class = 'uvicorn.workers.UvicornWorker'
