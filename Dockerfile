# Development Stage
FROM python:3.9 AS development

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Run tests
RUN pytest -v

# Production Stage
FROM python:3.9

WORKDIR /app

COPY --from=development /app .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

ENV PORT=8000

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "-w", "4", "app:app"]
