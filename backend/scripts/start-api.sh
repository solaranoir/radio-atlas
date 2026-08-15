#!/usr/bin/env sh

set -eu

echo "Starting SolaraSphere: Radio Atlas API"

# When Alembic is added, migrations can be enabled here:
# alembic upgrade head

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
