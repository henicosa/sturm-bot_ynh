command = '__FINALPATH__/venv/bin/gunicorn'
pythonpath = '__FINALPATH__'
threads = 5
workers = 1
user = '__APP__'
bind = '127.0.0.1:__PORT__'
errorlog = '/var/log/__APP__/error.log'
accesslog = '/var/log/__APP__/access.log'
access_log_format = '%({X-Real-IP}i)s %({X-Forwarded-For}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = 'warning'
capture_output = True
