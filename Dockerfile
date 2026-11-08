# TECH-02: container image for the HMS web app. Owner: P2.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.lock .
RUN pip install --only-binary :all: --require-hashes -r requirements.lock

# Copy only the app code, never the whole build context.
COPY manage.py .
COPY hms ./hms
COPY accounts ./accounts
COPY rooms ./rooms
COPY fees ./fees
COPY complaints ./complaints
COPY audit ./audit
COPY security ./security
COPY templates ./templates
COPY static ./static

# Run as a normal user, not root.
RUN useradd --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
