chdir = '/root/savop_back/protocol'
workers = 1
threads = 1
bind = '0.0.0.0:5000'
daemon = 'false'
worker_connections = 2000
pidfile = '/root/savop_back/log/gunicorn.pid'
loglevel = 'debug' 
