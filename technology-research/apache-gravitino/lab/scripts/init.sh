#!/bin/sh
set -eu
jar=postgresql-42.7.13.jar
digest=6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93
if ! echo "$digest  /drivers/$jar" | sha256sum -c - >/dev/null 2>&1; then
  curl --fail --location --retry 4 --connect-timeout 20 --max-time 240 \
    "https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.13/$jar" \
    --output "/drivers/$jar.tmp"
  echo "$digest  /drivers/$jar.tmp" | sha256sum -c -
  mv "/drivers/$jar.tmp" "/drivers/$jar"
fi
# Only this Compose project's named volumes are modified.
mkdir -p /raw-files/external/incoming /raw-files/managed
if [ ! -f /raw-files/external/incoming/events.jsonl ]; then
  cp /lab/data/events.jsonl /raw-files/external/incoming/events.jsonl
fi
chown -R 1000:0 /entity-store /raw-files
chmod 755 /drivers
chmod 644 "/drivers/$jar"
echo 'PASS: JDBC driver checksum and lab storage initialized.'
