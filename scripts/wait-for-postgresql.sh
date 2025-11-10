#!/bin/sh
set -e

echo "Aguardando o PostgreSQL iniciar em $POSTGRES_HOST:$POSTGRES_PORT..."

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    sleep 1
done

echo "PostgreSQL está pronto!"
exec "$@"
