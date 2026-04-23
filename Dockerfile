FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# The second stage isn't strictly necessary since the context already
# contains the Django project at the root.  If you want a smaller image
# you can keep a multistage build but make sure the path matches the
# repository layout.  The original COPY backend failed because there is
# no `backend` subdirectory; the project lives in the build context root.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# copy entire context instead of a non‑existent "backend" directory
COPY . .

# if you prefer to copy only the Django project, adjust the path to
# point at the correct folder (e.g. `COPY . .` or `COPY manage.py ./`).

# keep working directory at /app so the manage.py command works
WORKDIR /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

