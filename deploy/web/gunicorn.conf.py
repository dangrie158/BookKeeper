workers = 4
access_log_format = "%({x-forwarded-for}i)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'"
bind = "unix:/run/gunicorn/socket"
