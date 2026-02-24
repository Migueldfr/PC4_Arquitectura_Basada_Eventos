import json
import boto3
import random
from datetime import datetime

# ============ CONFIGURACIÓN ============
TOPIC_ARN = 'arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:SNSWeatherEvents'  # ⚠️ CAMBIA ESTO por tu ARN
REGION = 'eu-central-1'

sns = boto3.client('sns', region_name=REGION)

# ============ FUNCIONES DE GENERACIÓN ============
def generar_evento_temperatura():
    """Genera evento de temperatura aleatoria"""
    temp_value = round(random.uniform(-60, 50), 2)
    
    if temp_value < -50:
        status = "EXTREME_COLD"
    elif temp_value < 0:
        status = "COLD"
    elif temp_value < 25:
        status = "NORMAL"
    elif temp_value < 35:
        status = "HOT"
    else:
        status = "EXTREME_HEAT"
    
    return {
        'eventId': str(random.randint(10000, 99999)),
        'eventType': 'temperature-sensor',
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'sensorId': f'temp{random.randint(1000, 9999)}',
            'value': temp_value,
            'unit': 'Cº',
            'status': status
        }
    }

def generar_evento_viento():
    """Genera evento de viento aleatorio"""
    speed = round(random.uniform(0, 120), 1)
    
    if speed < 20:
        status = "CALM"
    elif speed < 40:
        status = "MODERATE"
    elif speed < 60:
        status = "STRONG"
    elif speed < 90:
        status = "EXTREME"
    else:
        status = "STORM"
    
    return {
        'eventId': str(random.randint(10000, 99999)),
        'eventType': 'wind-sensor',
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'sensorId': f'wind-{random.randint(1000, 9999)}',
            'speed': speed,
            'speedUnit': 'km/h',
            'direction': random.choice(['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']),
            'gust': round(speed * random.uniform(1.2, 1.8), 1),
            'status': status
        }
    }

def generar_evento_calidad_aire():
    """Genera evento de calidad del aire aleatorio"""
    aqi = random.randint(0, 500)
    
    if aqi <= 50:
        category = "BUENA"
    elif aqi <= 100:
        category = "MODERADA"
    elif aqi <= 150:
        category = "INSALUBRE_GRUPOS"
    elif aqi <= 200:
        category = "INSALUBRE"
    elif aqi <= 300:
        category = "MUY_INSALUBRE"
    else:
        category = "PELIGROSA"
    
    return {
        'eventId': str(random.randint(10000, 99999)),
        'eventType': 'AirQuality-sensor',
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'sensorId': f'air-{random.randint(1000, 9999)}',
            'aqi': aqi,
            'pm25': round(random.uniform(0, 300), 2),
            'pm10': round(random.uniform(0, 400), 2),
            'category': category
        }
    }

def generar_evento_visibilidad():
    """Genera evento de visibilidad aleatorio"""
    distance = random.randint(50, 10000)
    
    if distance < 200:
        condition = "CRITICAL"
    elif distance < 1000:
        condition = "VERY_LOW"
    elif distance < 4000:
        condition = "MODERATE"
    else:
        condition = "GOOD"
    
    return {
        'eventId': str(random.randint(10000, 99999)),
        'eventType': 'visibility-sensor',
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'sensorId': f'vis-{random.randint(1000, 9999)}',
            'distance': distance,
            'unit': 'meters',
            'condition': condition
        }
    }

# ============ LAMBDA HANDLER ============
def lambda_handler(event, context):
    """
    Genera un evento aleatorio de clima y lo publica en SNS.
    Se ejecuta automáticamente cada X minutos vía EventBridge Scheduler.
    """
    
    # Generar evento aleatorio
    generadores = [
        generar_evento_temperatura,
        generar_evento_viento,
        generar_evento_calidad_aire,
        generar_evento_visibilidad
    ]
    
    generador = random.choice(generadores)
    clima_event = generador()
    
    event_type = clima_event['eventType']
    
    # Publicar en SNS
    try:
        response = sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(clima_event),
            Subject=f'Evento Clima: {event_type}',
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': event_type
                }
            }
        )
        
        print(f"✅ Evento enviado: {event_type} - MessageId: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Evento publicado exitosamente',
                'eventType': event_type,
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        print(f"❌ Error publicando evento: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
