import random
from datetime import datetime
import uuid
import time
import boto3
import json



def get_temperature_status(value):
    if value <= -30:
        return "EXTREME_COLD"
    elif value <= -10:
        return "VERY_COLD"
    elif value <= 5:
        return "COLD"
    elif value <= 20:
        return "NORMAL"
    elif value <= 30:
        return "WARM"
    elif value <= 40:
        return "HOT"
    else:
        return "EXTREME_HEAT"

def get_aqi(aqi):
    if aqi <= 50:
        return "BUENA"
    elif aqi <= 100:
        return "MODERADA"
    elif aqi <= 150:
        return "INSALUBRE_PARA_SENSIBLES"
    elif aqi <= 200:
        return "INSALUBRE"
    elif aqi <= 300:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"

def get_pm25(pm25):
    if pm25 <= 12.0:
        return "BUENA"
    elif pm25 <= 35.4:
        return "MODERADA"
    elif pm25 <= 55.4:
        return "INSALUBRE_PARA_SENSIBLES"
    elif pm25 <= 150.4:
        return "INSALUBRE"
    elif pm25 <= 250.4:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"

def get_pm10(pm10):
    if pm10 <= 54:
        return "BUENA"
    elif pm10 <= 154:
        return "MODERADA"
    elif pm10 <= 254:
        return "INSALUBRE_PARA_SENSIBLES"
    elif pm10 <= 354:
        return "INSALUBRE"
    elif pm10 <= 424:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"

def get_visibility_condition(distance):
    if distance >= 10000:
        return "CLEAR"
    elif distance >= 4000:
        return "GOOD"
    elif distance >= 1000:
        return "MODERATE"
    elif distance >= 200:
        return "LOW"
    elif distance >= 50:
        return "VERY_LOW"
    else:
        return "CRITICAL"

def get_air_quality_category(aqi, pm25, pm10):
    categories = [
        get_aqi(aqi),
        get_pm25(pm25),
        get_pm10(pm10)
    ]

    severity_order = [
    "BUENA",
    "MODERADA",
    "INSALUBRE_PARA_SENSIBLES",
    "INSALUBRE",
    "MUY_INSALUBRE",
    "PELIGROSA"
    ]

    return max(categories, key=lambda c: severity_order.index(c))

def get_wind_status(speed, gust):
    #velocidad
    if speed <= 1:
        status = "CALM"
    elif speed <= 5:
        status = "LIGHT"
    elif speed <= 11:
        status = "BREEZE"
    elif speed <= 19:
        status = "MODERATE"
    elif speed <= 28:
        status = "FRESH"
    elif speed <= 38:
        status = "STRONG"
    elif speed <= 49:
        status = "VERY_STRONG"
    elif speed <= 61:
        status = "STORM"
    else:
        status = "EXTREME"

    #ráfaga
    if gust >= 70:
        return "EXTREME"
    elif gust >= 50 and status not in ["STORM", "EXTREME"]:
        return "STORM"
    elif gust >= 30 and status in ["CALM", "LIGHT", "BREEZE"]:
        return "MODERATE"

    return status


client_sns = boto3.client("sns", region_name="eu-central-1")

def generate_event():
    """Genera un evento aleatorio con valores frescos en cada llamada"""
    
    # Generar valores aleatorios
    temperature_value = round(random.uniform(-70, 50), 2)
    aqi_value = random.randint(0, 350)
    pm25_value = round(random.uniform(0, 300), 2)
    pm10_value = round(random.uniform(0, 500), 2)
    distance_value = round(random.uniform(0, 10000))
    speed_value = round(random.uniform(0, 62), 1)
    gust_value = round(random.uniform(0, 70), 1)
    
    # Crear eventos con nuevos IDs y timestamps
    sensor_temp = {
        "eventId": str(uuid.uuid4()),
        "eventType": "temperature-sensor",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "data": {
            "sensorId": "temp" + str(random.randint(1, 10000)),
            "value": temperature_value,
            "unit": "Cº",
            "status": get_temperature_status(temperature_value)
        }
    }
    
    sensor_air = {
        "eventId": str(uuid.uuid4()),
        "eventType": "AirQuality-sensor",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "data": {
            "sensorId": "air-" + str(random.randint(1, 10000)),
            "aqi": aqi_value,
            "pm25": pm25_value,
            "pm10": pm10_value,
            "category": get_air_quality_category(aqi_value, pm25_value, pm10_value)
        }
    }
    
    sensor_visibility = {
        "eventId": str(uuid.uuid4()),
        "eventType": "visibility-sensor",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "data": {
            "sensorId": "vis-" + str(random.randint(1, 10000)),
            "distance": distance_value,
            "unit": "meters",
            "condition": get_visibility_condition(distance_value)
        }
    }
    
    sensor_wind = {
        "eventId": str(uuid.uuid4()),
        "eventType": "wind-sensor",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "data": {
            "sensorId": "wind-" + str(random.randint(1, 10000)),
            "speed": speed_value,
            "speedUnit": "km/h",
            "direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "gust": gust_value,
            "status": get_wind_status(speed_value, gust_value)
        }
    }
    
    return random.choice([sensor_air, sensor_temp, sensor_visibility, sensor_wind])

while True:
    event = generate_event()
    
    # IMPORTANTE: Enviamos eventType como MessageAttribute para que funcionen los filtros
    client_sns.publish(
        Message=json.dumps(event),
        TargetArn="arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherEvents",
        MessageAttributes={
            'eventType': {
                'DataType': 'String',
                'StringValue': event['eventType']
            }
        }
    )
    print("Evento enviado:", event)
    time.sleep(0.5)  # streaming continuo


