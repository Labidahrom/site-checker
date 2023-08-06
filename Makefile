PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) site_checker.wsgi:application & \
	poetry run celery -A site_checker worker --loglevel=info

app_start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) site_checker.wsgi:application

celery_start:
	poetry run celery -A site_checker worker --loglevel=info

makemigrations:
	poetry run python manage.py makemigrations site_checker

migrate:
	poetry run python manage.py migrate

lint:
	poetry run flake8 site_checker

test:
	poetry run python3 manage.py test