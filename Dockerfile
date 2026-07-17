FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY instagram_monitor_bot.py .
COPY instagram_monitor_data.json .

CMD ["python", "instagram_monitor_bot.py", "--once"]
