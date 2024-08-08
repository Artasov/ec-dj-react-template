#!/bin/sh

############
#   PROD   #
############
/usr/sbin/chronyd

echo "#####################################"
echo "######### Server Starting... ########"
echo "#####################################"

# shellcheck disable=SC2164
cd /srv/backend
echo "Collecting static files"
python manage.py collectstatic --noinput &&
  echo "Migrating"
python manage.py migrate
echo "Set public policy for media bucket"
python manage.py set_public_policy_media

supervisord -c /etc/supervisor/conf.d/supervisord.conf