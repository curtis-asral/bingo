# gunicorn.conf.py

import multiprocessing

# ----- Core settings -----
bind = "0.0.0.0:5000"
workers = 2 * multiprocessing.cpu_count() // 3 or 2  # a balanced rule of thumb
worker_class = "sync"
timeout = 60
graceful_timeout = 30

# ----- Development convenience -----
reload = True  # reload when code changes
reload_extra_files = ["app.py"]  # optional: specify key files to watch

# ----- Logging -----
accesslog = "-"   # stdout
errorlog = "-"    # stdout
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# ----- Process management -----
max_requests = 1000
max_requests_jitter = 50  # helps prevent worker synchronization issues

# ----- Reliability -----
preload_app = True  # load app before forking workers
