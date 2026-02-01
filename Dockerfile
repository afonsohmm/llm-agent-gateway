# Stage 1: Build the application
FROM python:3.11-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies (skip installing the project itself; source is copied later)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Stage 2: Create the final image
FROM python:3.11-slim

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /app /app

# Copy the application code
COPY ./app /app/app

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
