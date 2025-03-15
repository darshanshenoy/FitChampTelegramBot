from googleapiclient.discovery import build
import sqlite3
from datetime import datetime, timedelta
import database


def extract_value(data, value_type):
    try:
        return data["bucket"][0]["dataset"][0]["point"][0]["value"][0][value_type]
    except (IndexError, KeyError):
        return 0


def fetch_health_data(telegram_id, creds):
    service = build("fitness", "v1", credentials=creds)
    now = datetime.now()
    start_time = now - timedelta(days=1)  # Last 24 hours
    start_time_millis = int(start_time.timestamp() * 1000)
    end_time_millis = int(now.timestamp() * 1000)

    # Fetch steps
    steps_data = service.users().dataset().aggregate(
        userId="me",
        body={
            "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    ).execute()
    steps = extract_value(steps_data, "intVal")

    # Fetch calories
    calories_data = service.users().dataset().aggregate(
        userId="me",
        body={
            "aggregateBy": [{"dataTypeName": "com.google.calories.expended"}],
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    ).execute()
    calories = extract_value(calories_data, "fpVal")

    # Fetch distance
    distance_data = service.users().dataset().aggregate(
        userId="me",
        body={
            "aggregateBy": [{"dataTypeName": "com.google.distance.delta"}],
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    ).execute()
    distance = extract_value(distance_data, "fpVal")

    # Store in database
    conn = sqlite3.connect("health_data.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO health_data (telegram_id, date, steps, calories, distance) VALUES (?, ?, ?, ?, ?)",
              (telegram_id, now.strftime("%Y-%m-%d"), steps, calories, distance))
    conn.commit()
    conn.close()

    return steps, calories, distance