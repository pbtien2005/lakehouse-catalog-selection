#!/bin/bash
set -euo pipefail
# Catalog providers have isolated classloaders: the driver belongs here.
ln -sf /drivers/postgresql-42.7.13.jar \
  /opt/gravitino/catalogs/jdbc-postgresql/libs/postgresql-42.7.13.jar
exec /bin/bash /opt/gravitino/docker/docker-entrypoint.sh
