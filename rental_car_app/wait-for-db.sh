#!/bin/sh

# wait-for-db.sh

set -e

host="$1"
shift
cmd="$@"

until mysql -h "$host" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e 'select 1' > /dev/null 2>&1; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 2
done

>&2 echo "MySQL is up - executing command"
exec $cmd
