#!/bin/sh

EMBY_ADDRESS=${EMBY_ADDRESS}
echo ${EMBY_ADDRESS}
envsubst '$EMBY_ADDRESS' < /etc/nginx/conf.d/emby.conf.template > /etc/nginx/conf.d/emby.conf
cat /etc/nginx/conf.d/emby.conf

if [ $# = 0 ]
then
    exec nginx -g 'daemon off;'
else
    exec "$@"
fi