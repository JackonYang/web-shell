env_file='../../.private-data/web-shell.env'

if [ -f "$env_file" ]; then
    env $(cat $env_file | xargs) python3 manage.py runserver 0.0.0.0:18000
else
    python3 manage.py runserver 0.0.0.0:18000
fi
