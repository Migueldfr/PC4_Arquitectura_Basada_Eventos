import sqlite3

# Configuración
DB_NAME = "clima_local.db"

def create_local_tables():
    print(f"--- Configuración Base de Datos Local ({DB_NAME}) ---")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # TABLA 1: ALPINISTA (Interesa: Temperatura y Viento)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alpinista_data (
                event_id TEXT PRIMARY KEY,
                event_type TEXT, -- temperature-sensor, wind-sensor
                valor REAL,
                unidad TEXT,
                status TEXT, -- EXTREME_COLD, STORM...
                timestamp_ingesta DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("✅ Tabla creada: 'alpinista_data'")

        # TABLA 2: CICLISTA (Interesa: Visibilidad y Aire)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciclista_data (
                event_id TEXT PRIMARY KEY,
                event_type TEXT, -- visibility-sensor, AirQualit-sensor
                valor REAL,
                unidad TEXT,
                status TEXT,
                timestamp_ingesta DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("✅ Tabla creada: 'ciclista_data'")

        # TABLA 3: DRON (Interesa: Viento y Visibilidad)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dron_data (
                event_id TEXT PRIMARY KEY,
                event_type TEXT, -- wind-sensor, visibility-sensor
                valor REAL,
                unidad TEXT,
                status TEXT,
                timestamp_ingesta DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        print("✅ Tabla creada: 'dron_data'")
        
        conn.commit()
        print(f"\n✅ Archivo {DB_NAME} listo para DBeaver.")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    create_local_tables()
