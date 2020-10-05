#!/bin/sh

set -e

if [ "$BACKUP_MODE" != "none" ]; then
  /backup.sh
fi

if [ ! -f /etc/cron.d/feed-update ]; then
  cat << EOF > /etc/cron.d/feed-update
*/10 * * * * root /usr/bin/curl --silent https://blog.kivy.org/?update_feedwordpress=1

EOF
  chmod 0644 /etc/cron.d/feed-update
fi

/etc/init.d/cron restart
php-fpm
