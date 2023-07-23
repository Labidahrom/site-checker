PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) site_checker.wsgi:application

debug start:
	poetry run python manage.py runserver

makemigrations:
	poetry run python manage.py makemigrations site_checker

migrate:
	poetry run python manage.py migrate