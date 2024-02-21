# Development Stage
FROM python:3.9 AS development
ARG MYSQL_HOST
ARG MYSQL_USER
ARG MYSQL_PASSWORD
ARG MYSQL_DATABASE

ENV MYSQL_HOST=${MYSQL_HOST}
ENV MYSQL_USER=${MYSQL_USER}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}
ENV MYSQL_DATABASE=${MYSQL_DATABASE}

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Run tests
# RUN pytest -v


# Production Stage
FROM python:3.9

WORKDIR /app

COPY --from=development /app .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

ENV PORT=8000

# 
CMD ["python", "app.py"]
