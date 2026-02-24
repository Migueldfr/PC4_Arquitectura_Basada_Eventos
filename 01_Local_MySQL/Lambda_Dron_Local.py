import boto3
import json
import mysql.connector
import time
import random
from datetime import datetime
#from decimal import Decimal

# ============ CLIENTES AWS ============
sqs = boto3.client('sqs', region_name='eu-central-1')
cloudwatch = boto3.client('cloudwatch', region_name='eu-central-1')

def simular_fallo_aleatorio():
    """Simula un fallo si el número aleatorio es par Y mayor a 80 (~10% de probabilidad)"""
    numero = random.randint(1, 100)  # Genera un número entre 1 y 100
    if numero % 2 == 0 and numero > 80:  # Si es par Y > 80 (82, 84, 86, 88, 90, 92, 94, 96, 98, 100)
        raise Exception(f"💥 [CHAOS MONKEY] Fallo simulado (número par > 80: {numero})")

def procesar_alarma(event_id, event_type, valor, unidad, status, timestamp_evento):
    """Envía métrica a CloudWatch Y guarda en MySQL si detecta condición extrema"""
    condiciones_extremas = ["EXTREME_COLD", "EXTREME_HEAT", "EXTREME", "STORM","CRITICAL","PELIGROSA","VERY_LOW"]
    
    if status not in condiciones_extremas:
        return
    
    # 1. Enviar a CloudWatch
    try:
        cloudwatch.put_metric_data(
            Namespace='WeatherEvents/Dron',
            MetricData=[{
                'MetricName': 'AlertaExtrema',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow(),
                'Dimensions': [
                    {'Name': 'EventType', 'Value': event_type},
                    {'Name': 'Status', 'Value': status}
                ]
            }]
        )
        print(f"🚨 [CLOUDWATCH] Alarma enviada: {event_type} - {status} ({valor} {unidad})")
    except Exception as e:
        print(f"⚠️  Error enviando a CloudWatch: {e}")
    
    # 2. Guardar en MySQL
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alarmas (event_id, event_type, timestamp, valor, unidad, status, consumidor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE event_id=event_id
        ''', (event_id, event_type, timestamp_evento, valor, unidad, status, 'Dron'))
        conn.commit()
        conn.close()
        print(f"💾 [MYSQL] Alarma guardada en tabla 'alarmas'")
    except Exception as e:
        print(f"⚠️  Error guardando alarma en MySQL: {e}")

# ============ CONFIGURACIÓN ============
# URL de la Cola SQS del Dron
QUEUE_URL = "https://sqs.eu-central-1.amazonaws.com/TU_ACCOUNT_ID/weather_dron" 

REGION = "eu-central-1"

# MySQL Local
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "pc4_clima_events",
    "port": 3306
}

# ============ LÓGICA ESPECÍFICA ============
# El Dron procesa Viento y Visibilidad
TARGET_TABLE = "dron_data"
ALLOWED_EVENTS = ["wind-sensor", "visibility-sensor"]

# ============ FUNCIONES ============
def get_mysql_connection():
    return mysql.connector.connect(**DB_CONFIG)

def extract_data(clima_event):
    """Extrae valor, unidad y status según el tipo de evento"""
    event_type = clima_event.get('eventType')
    data = clima_event.get('data', {})
    
    valor = None
    unidad = "index"
    status = data.get('status')

    if event_type == "wind-sensor":
        valor = data.get('speed')
        unidad = data.get('speedUnit')
    elif event_type == "visibility-sensor":
        valor = data.get('distance')
        unidad = data.get('unit')
        status = data.get('condition') # Para visibilidad usa condition
    
    return valor, unidad, status

def guardar_en_mysql(clima_event):
    event_type = clima_event.get('eventType')
    
    if event_type not in ALLOWED_EVENTS:
        print(f"⚠️  Ignorando evento no relevante para Dron: {event_type}")
        return
    # probamos a generar un fallo aleatorio
    simular_fallo_aleatorio()

    try:
        event_id = clima_event.get('eventId')
        timestamp_evento = clima_event.get('timestamp')
        valor, unidad, status = extract_data(clima_event)
        
        # Procesar alarma (CloudWatch + MySQL) si es condición extrema
        procesar_alarma(event_id, event_type, valor, unidad, status, timestamp_evento)
        
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            INSERT INTO {TARGET_TABLE} (event_id, event_type, valor, unidad, status)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE event_id=event_id
        ''', (event_id, event_type, valor, unidad, status))
        
        conn.commit()
        conn.close()
        print(f"✅ [Dron] Guardado: {event_type} - {valor} {unidad}")
        
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("=" * 50)
    print("🚁 LAMBDA LOCAL: DRON")
    print("=" * 50)
    print(f"Escuchando: {QUEUE_URL}")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )
            
            if 'Messages' in response:
                for message in response['Messages']:
                    try:
                        # Parsear mensaje SNS -> SQS
                        body = json.loads(message['Body'])
                        clima_event = json.loads(body['Message'])
                        
                        print(f"\n📩 Recibido: {clima_event.get('eventType')}")
                        guardar_en_mysql(clima_event)
                    
                        # ACK
                        sqs.delete_message(
                            QueueUrl=QUEUE_URL,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                    except Exception as e:
                        print(f"❌ Error procesando mensaje: {e}")
            else:
                print(".", end="", flush=True)
                
        except KeyboardInterrupt:
            print("\n🛑 Detenido.")
            break
        except Exception as e:
            print(f"\n❌ Error polling: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
