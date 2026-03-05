FROM mcr.microsoft.com/playwright/python:v1.58.0-focal

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install --with-deps chromium

CMD ["python", "run_scraper.py"]