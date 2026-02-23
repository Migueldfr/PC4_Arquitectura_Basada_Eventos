import boto3
from datetime import datetime

# Cliente CloudWatch
cloudwatch = boto3.client('cloudwatch', region_name='eu-central-1')

def enviar_metrica_prueba():
    """Envía una métrica de prueba a CloudWatch"""
    try:
        response = cloudwatch.put_metric_data(
            Namespace='WeatherEvents/Test',  # Namespace personalizado
            MetricData=[
                {
                    'MetricName': 'EventoExtremoTest',
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'EventType', 'Value': 'temperature-sensor'},
                        {'Name': 'Status', 'Value': 'EXTREME_COLD'}
                    ]
                }
            ]
        )
        print("✅ Métrica enviada correctamente a CloudWatch")
        print(f"Response: {response}")
        print("\n📊 Ve a AWS Console → CloudWatch → Métricas → WeatherEvents/Test")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️ Verifica:")
        print("  - Credenciales AWS configuradas (aws configure)")
        print("  - Permisos CloudWatch (cloudwatch:PutMetricData)")

if __name__ == "__main__":
    print("🧪 Prueba de CloudWatch - Enviando métrica...")
    enviar_metrica_prueba()