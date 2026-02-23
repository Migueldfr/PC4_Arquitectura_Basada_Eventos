import json
import boto3
import random
from datetime import datetime
from decimal import Decimal
import os

# ============ CLIENTES AWS ============
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

# ============ CONFIGURACIÓN (Variables de Entorno) ============
TABLE_NAME = os.environ.get('TABLE_NAME', 'ciclista_events')
ALARMAS_TABLE = os.environ.get('ALARMAS_TABLE', 'weather_alarmas')
ALLOWED_EVENTS = os.environ.get('ALLOWED_EVENTS', 'AirQuality-sensor,visibility-sensor').split(',')
CONSUMIDOR = os.environ.get('CONSUMIDOR', 'Ciclista')
ALERT_TOPIC_ARN = os.environ.get('ALERT_TOPIC_ARN', '')

table = dynamodb.Table(TABLE_NAME)
alarmas_table = dynamodb.Table(ALARMAS_TABLE)

# ============ FUNCIONES ============
def simular_fallo_aleatorio():
    """Simula un fallo aleatorio (~10% probabilidad) para testing de reintentos"""
    numero = random.randint(1, 100)
    if numero % 2 == 0 and numero > 80:
        raise Exception(f"💥 [CHAOS MONKEY] Fallo simulado (número par > 80: {numero})")

def procesar_alarma(item):
    """Envía métrica a CloudWatch y guarda en tabla alarmas si es condición extrema"""
    condiciones_extremas = [
        "EXTREME_COLD", "EXTREME_HEAT", "EXTREME", "STORM",
        "CRITICAL", "PELIGROSA", "MUY_INSALUBRE", "INSALUBRE", "VERY_LOW"
    ]
    
    status = item.get('data', {}).get('status')
    
    if status not in condiciones_extremas:
        return
    
    # 1. CloudWatch
    try:
        cloudwatch.put_metric_data(
            Namespace=f'WeatherEvents/{CONSUMIDOR}',
            MetricData=[{
                'MetricName': 'AlertaExtrema',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow(),
                'Dimensions': [
                    {'Name': 'EventType', 'Value': item.get('eventType')},
                    {'Name': 'Status', 'Value': status}
                ]
            }]
        )
        print(f"🚨 [CLOUDWATCH] Alarma enviada: {item.get('eventType')} - {status}")
    except Exception as e:
        print(f"⚠️  Error enviando a CloudWatch: {e}")
    
    # 2. DynamoDB alarmas
    try:
        alarma_item = {
            'event_id': item.get('eventId'),
            'created_at': datetime.utcnow().isoformat(),
            'event_type': item.get('eventType'),
            'timestamp': item.get('timestamp'),
            'valor': item.get('data', {}).get('value'),
            'unidad': item.get('data', {}).get('unit'),
            'status': status,
            'consumidor': CONSUMIDOR
        }
        alarma_item = json.loads(json.dumps(alarma_item), parse_float=Decimal)
        alarmas_table.put_item(Item=alarma_item)
        print(f"💾 [DYNAMODB] Alarma guardada en tabla '{ALARMAS_TABLE}'")
    except Exception as e:
        print(f"⚠️  Error guardando alarma: {e}")
    
    # 3. Enviar notificación por email vía SNS
    if ALERT_TOPIC_ARN:
        try:
            valor = item.get('data', {}).get('value') or item.get('data', {}).get('speed') or item.get('data', {}).get('aqi') or item.get('data', {}).get('distance')
            unidad = item.get('data', {}).get('unit') or item.get('data', {}).get('speedUnit') or 'AQI' if item.get('data', {}).get('aqi') else 'meters'
            
            subject = f'🚨 ALERTA EXTREMA [{CONSUMIDOR}]: {status}'
            message = (
                f"⚠️ ALERTA METEOROLÓGICA EXTREMA\n"
                f"{'='*40}\n"
                f"Consumidor: {CONSUMIDOR}\n"
                f"Tipo Sensor: {item.get('eventType')}\n"
                f"Estado: {status}\n"
                f"Valor: {valor} {unidad}\n"
                f"Sensor ID: {item.get('data', {}).get('sensorId')}\n"
                f"Timestamp: {item.get('timestamp')}\n"
                f"Event ID: {item.get('eventId')}\n"
                f"{'='*40}\n"
                f"Sistema de Monitorización Climática IoT - PC4"
            )
            
            sns.publish(
                TopicArn=ALERT_TOPIC_ARN,
                Subject=subject[:100],
                Message=message
            )
            print(f"📧 [EMAIL] Notificación enviada: {status}")
        except Exception as e:
            print(f"⚠️  Error enviando email: {e}")

def lambda_handler(event, context):
    """Handler principal de AWS Lambda"""
    print(f"🚴 [{CONSUMIDOR}] Procesando batch de {len(event['Records'])} mensajes")
    
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            message = json.loads(body['Message']) if 'Message' in body else body
            
            event_type = message.get('eventType')
            event_id = message.get('eventId', 'unknown')[:8]
            
            print(f"📩 Recibido [{event_id}]: {event_type}")
            
            if event_type not in ALLOWED_EVENTS:
                print(f"⚠️  Ignorando evento no permitido: {event_type}")
                continue
            
            simular_fallo_aleatorio()
            
            item = json.loads(json.dumps(message), parse_float=Decimal)
            
            # Mapear campos
            item['event_id'] = item.get('eventId')
            item['event_type'] = item.get('eventType')
            
            procesar_alarma(item)
            
            table.put_item(Item=item)
            print(f"✅ [{CONSUMIDOR}] Guardado: {event_type} - {event_id}")
            
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            raise
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Procesados {len(event["Records"])} eventos por {CONSUMIDOR}')
    }
