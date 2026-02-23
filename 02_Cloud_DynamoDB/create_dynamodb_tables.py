#!/usr/bin/env python3
"""
Script para crear las tablas DynamoDB necesarias para el proyecto PC4
Ejecutar: python create_dynamodb_tables.py
"""

import boto3
from botocore.exceptions import ClientError

# Configuración
REGION = 'eu-central-1'

# Cliente DynamoDB
dynamodb = boto3.client('dynamodb', region_name=REGION)

def create_table(table_name, add_gsi=False):
    """Crea una tabla DynamoDB con el esquema estándar"""
    
    try:
        # Esquema base
        params = {
            'TableName': table_name,
            'KeySchema': [
                {'AttributeName': 'event_id', 'KeyType': 'HASH'},   # Partition key
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}  # Sort key
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'event_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'  # On-demand (Free Tier friendly)
        }
        
        # Añadir GSI para tabla de alarmas
        if add_gsi:
            params['AttributeDefinitions'].append(
                {'AttributeName': 'consumidor', 'AttributeType': 'S'}
            )
            params['AttributeDefinitions'].append(
                {'AttributeName': 'created_at', 'AttributeType': 'S'}
            )
            params['GlobalSecondaryIndexes'] = [
                {
                    'IndexName': 'consumidor-created_at-index',
                    'KeySchema': [
                        {'AttributeName': 'consumidor', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ]
        
        response = dynamodb.create_table(**params)
        print(f"✅ Tabla '{table_name}' creada exitosamente")
        print(f"   ARN: {response['TableDescription']['TableArn']}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Tabla '{table_name}' ya existe")
            return False
        else:
            print(f"❌ Error creando tabla '{table_name}': {e}")
            raise

def wait_for_table(table_name):
    """Espera a que la tabla esté activa"""
    print(f"⏳ Esperando a que '{table_name}' esté activa...")
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name)
    print(f"✅ Tabla '{table_name}' activa y lista")

def main():
    print("=" * 60)
    print("🚀 Creación de Tablas DynamoDB - Proyecto PC4")
    print("=" * 60)
    print(f"Región: {REGION}\n")
    
    # Tablas a crear
    tables = [
        ('alpinista_events', False),
        ('dron_events', False),
        ('ciclista_events', False),
        ('weather_alarmas', True)  # Con GSI
    ]
    
    created_tables = []
    
    for table_name, add_gsi in tables:
        if create_table(table_name, add_gsi):
            created_tables.append(table_name)
    
    # Esperar a que todas las tablas estén activas
    if created_tables:
        print(f"\n{'='*60}")
        print("⏳ Esperando a que las tablas estén activas...")
        print(f"{'='*60}\n")
        
        for table_name in created_tables:
            wait_for_table(table_name)
    
    print(f"\n{'='*60}")
    print("✅ COMPLETADO - Resumen de Tablas")
    print(f"{'='*60}")
    
    # Listar todas las tablas
    response = dynamodb.list_tables()
    pc4_tables = [t for t in response['TableNames'] if 'events' in t or 'alarmas' in t]
    
    for table_name in pc4_tables:
        table_info = dynamodb.describe_table(TableName=table_name)
        status = table_info['Table']['TableStatus']
        item_count = table_info['Table']['ItemCount']
        print(f"  • {table_name}")
        print(f"    Estado: {status} | Elementos: {item_count}")
    
    print(f"\n{'='*60}")
    print("📝 Próximos Pasos:")
    print(f"{'='*60}")
    print("1. Ve a AWS Lambda Console")
    print("2. Crea 3 funciones Lambda (ProcessAlpinista, ProcessDron, ProcessCiclista)")
    print("3. Sube el código de Lambda_*_Cloud.py a cada función")
    print("4. Configura las variables de entorno según el README")
    print("5. Añade trigger SQS a cada Lambda")
    print("6. ¡Ejecuta el Producer y observa CloudWatch Logs!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
