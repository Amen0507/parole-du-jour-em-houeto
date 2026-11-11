FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système et les polices
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rendre exécutables les scripts
RUN chmod +x scripts/*.py scripts/*.sh

EXPOSE 8080

CMD ["python3", "app.py"]
