# 🧪 Guía de Ejecución Local (MySQL)

Esta carpeta contiene todo lo necesario para simular la **Arquitectura de Eventos Distribuida** en tu ordenador, sin necesidad de gastar dinero en Lambdas o DynamoDB todavía.

## 📋 Requisitos Previos

1.  **Python** instalado (con `boto3` y `mysql-connector-python`).
2.  **MySQL Server** corriendo (XAMPP, Docker, o local).
3.  **Credenciales AWS** configuradas (`.aws/credentials` o variables de entorno).
4.  **Infraestructura AWS Creada**:
    *   1 SNS Topic (`WeatherEventsTopic`).
    *   3 SQS Queues (`weather_alpinista`, `weather_ciclista`, `weather_dron`).
    *   3 Suscripciones SNS->SQS (con los filtros configurados).

---

## 🚀 Pasos para Ejecutar

### Paso 1: Preparar la Base de Datos
*(Solo necesitas hacer esto la primera vez)*

1.  Abre una terminal en esta carpeta (`01_Local_MySQL`).
2.  Ejecuta el script de setup:
    ```bash
    python setup_local_mysql.py
    ```
    *   Verás: `✅ Base de datos verificada...`, `✅ Tabla creada...`

### Paso 2: Encender los Consumidores ("Lambdas")
Vamos a simular que tenemos 3 Lambdas escuchando permanentemente. Para ver el efecto, **necesitas 3 terminales distintas**.

*   **Terminal A (Alpinista):**
    ```bash
    python Lambda_Alpinista_Local.py
    ```
    *(Verás: `🏔️ LAMBDA LOCAL: ALPINISTA - Escuchando...`)*

*   **Terminal B (Ciclista):**
    ```bash
    python Lambda_Ciclista_Local.py
    ```
    *(Verás: `🚴 LAMBDA LOCAL: CICLISTA - Escuchando...`)*

*   **Terminal C (Dron):**
    ```bash
    python Lambda_Dron_Local.py
    ```
    *(Verás: `🚁 LAMBDA LOCAL: DRON - Escuchando...`)*

### Paso 3: Generar Eventos (El "Productor")
Ahora, vamos a enviar datos al sistema.

1.  Abre una **4ª Terminal**.
2.  Ejecuta el productor:
    ```bash
    python SNS_Producer_events.py
    ```

### Paso 4: Observar la Magia ✨

1.  Verás en la **Terminal 4** que se envían eventos (`temperature`, `wind`, `visibility`, etc.).
2.  **¡Mira las otras terminales!**
    *   Si sale `temperature` -> Solo se mueve la **Terminal A** (Alpinista).
    *   Si sale `visibility` -> Se mueven la **Terminal B** (Ciclista) y **C** (Dron).
    *   Si sale `wind` -> Se mueven la **Terminal A** y **C**.
    
    *Esto demuestra que el filtrado SNS -> SQS está funcionando perfectamente.*

### Paso 5: Verificar Datos (SQL)
Abre DBeaver o Workbench y consulta:

```sql
SELECT * FROM alpinista_data;
SELECT * FROM ciclista_data;
SELECT * FROM dron_data;
```
Verás que cada tabla tiene SOLO los datos que le interesan a esa persona.

---

## 🛠️ Solución de Problemas (General)

*   **Error "No module named..."**: Ejecuta `pip install boto3 mysql-connector-python`.
*   **Error Conexión MySQL**: Revisa `DB_CONFIG` (usuario `root`, pass `root` o la que tengas).
