FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code


COPY pyproject.toml /code/pyproject.toml
COPY alembic.ini /code/alembic.ini
COPY migrations /code/migrations
COPY app /code/app
COPY tests /code/tests
COPY scripts /code/scripts

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e ".[dev]" \
    && chmod +x /code/scripts/*.sh

EXPOSE 8000

CMD ["/code/scripts/start-api.sh"]
