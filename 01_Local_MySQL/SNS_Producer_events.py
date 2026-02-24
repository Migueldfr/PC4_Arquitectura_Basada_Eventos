import random
from datetime import datetime
import uuid
import time
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()



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


REGION = os.getenv("AWS_REGION", "eu-central-1")
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "TU_ACCOUNT_ID")

def main():
    client_sns = boto3.client("sns", region_name=REGION)
    print("Iniciando Productor de Eventos SNS...")
    
    while True:
        event = generate_event()
        
        # IMPORTANTE: Enviamos eventType como MessageAttribute para que funcionen los filtros
        client_sns.publish(
            Message=json.dumps(event),
            TargetArn=f"arn:aws:sns:{REGION}:{ACCOUNT_ID}:WeatherEvents",
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': event['eventType']
                }
            }
        )
        print("Evento enviado:", event)
        time.sleep(0.5)  # streaming continuo

if __name__ == "__main__":
    main()
