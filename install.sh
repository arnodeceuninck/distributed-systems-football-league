sudo docker-compose -f docker-compose-dev.yml up --build

sudo docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run clubs python manage.py recreate-db
sudo docker-compose -f docker-compose-dev.yml run matches python manage.py recreate-db

sudo docker-compose -f docker-compose-dev.yml run users python manage.py seed-db
sudo docker-compose -f docker-compose-dev.yml run clubs python manage.py seed-db
sudo docker-compose -f docker-compose-dev.yml run matches python manage.py seed-db