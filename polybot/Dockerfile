FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8443

ENV TELEGRAM_TOKEN telegram_token
ENV TELEGRAM_APP_URL telegram_app_url

CMD ["python3", "app.py"]