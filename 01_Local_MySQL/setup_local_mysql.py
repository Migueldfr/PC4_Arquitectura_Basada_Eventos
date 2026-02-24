import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno (ignora si no existe el archivo)
load_dotenv()

# CONFIGURACIÓN MYSQL
DB_CONFIG = {
    "host": "localhost",
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"), 
    "port": 3306
}

DB_NAME = "pc4_clima_events"

def create_mysql_tables():
    print("--- Configuración MySQL Local ---")
    
    try:
        # 1. Conectar al servidor (sin base de datos aún)
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 2. Crear Base de Datos
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Base de datos verificada: {DB_NAME}")
        
        # 3. Usar esa BD
        cursor.execute(f"USE {DB_NAME}")
        
        # 4. Crear Tablas (Syntax MySQL)
        
        # ALPINISTA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alpinista_data (
                event_id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(50),
                valor FLOAT,
                unidad VARCHAR(20),
                status VARCHAR(50),
                timestamp_ingesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla creada: alpinista_data")

        # CICLISTA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciclista_data (
                event_id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(50),
                valor FLOAT,
                unidad VARCHAR(20),
                status VARCHAR(50),
                timestamp_ingesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla creada: ciclista_data")

        # DRON
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dron_data (
                event_id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(50),
                valor FLOAT,
                unidad VARCHAR(20),
                status VARCHAR(50),
                timestamp_ingesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla creada: dron_data")
        
        # ALARMAS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarmas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE,
                event_type VARCHAR(50),
                timestamp TIMESTAMP,
                valor DECIMAL(10,2),
                unidad VARCHAR(20),
                status VARCHAR(50),
                consumidor VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla creada: alarmas")
        
        conn.commit()
        conn.close()
        
        print(f"\n[Listo] Ahora conecta DBeaver a: localhost -> {DB_NAME}")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    create_mysql_tables()
