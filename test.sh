sudo docker-compose -f docker-compose-dev.yml run users python manage.py test
sudo docker-compose -f docker-compose-dev.yml run clubs python manage.py test
sudo docker-compose -f docker-compose-dev.yml run matches python manage.py test
