# 📘 README: Configuración Total del Entorno Local

Este documento recopila **TODA** la configuración necesaria para que el sistema funcione. Si algo falla mañana, revisa esta lista de chequeo punto por punto.

---

## 1. Configuración en AWS (La Nube)

Para que los mensajes fluyan, AWS debe estar configurado **exactamente** así:

### A. Servicio SNS (El Megáfono)
*   **Topic Name**: `WeatherEventsTopic` (o similar).
*   **Tipo**: Standard.
*   **ARN**: Necesitas copiar este ARN (ej: `arn:aws:sns:eu-central-1:123456789:WeatherEventsTopic`).
    *   *¿Dónde se usa?* Se pega en el script `SNS_Producer_events.py` -> variable `TargetArn`.

### B. Servicio SQS (Los Buzones)
Debes tener **3 Colas Standard** creadas:
1.  `weather_alpinista`
2.  `weather_dron`
3.  `weather_ciclista`

*   **URLs**: Cada cola tiene una URL única (ej: `https://sqs.eu-central-1.amazonaws.com/123456789/weather_alpinista`).
    *   *¿Dónde se usan?* Se pegan en cada script `Lambda_X_Local.py` -> variable `QUEUE_URL`.
*   **Permissions (Access Policy)**: La cola debe permitir que SNS le envíe mensajes. AWS suele configurarlo solo si creas la suscripción desde SNS, pero si falla, asegúrate de que la Policy de la cola permita `sns:SendMessage` desde el ARN del Topic.

### C. Suscripciones SNS -> SQS (El Enrutado)
Aquí es donde ocurre la magia (y los errores). En el SNS Topic, debes tener **3 Suscripciones** activas, una para cada cola, con estos **FILTROS EXACTOS**:

#### 1. Para Cola `weather_alpinista`
*   **Filter Policy (Avanzado)**:
    ```json
    {
      "eventType": ["temperature-sensor", "wind-sensor"]
    }
    ```

#### 2. Para Cola `weather_dron`
*   **Filter Policy**:
    ```json
    {
      "eventType": ["wind-sensor", "visibility-sensor"]
    }
    ```

#### 3. Para Cola `weather_ciclista`
*   **Filter Policy** (¡Cuidado con el Typo!):
    ```json
    {
      "eventType": ["AirQuality-sensor", "visibility-sensor"]
    }
    ```
    *(Nota: El código Python debe enviar `AirQuality-sensor` exactamente igual. Si pones 'AirQualit' en uno y 'AirQuality' en otro, no llegará nada).*

---

## 2. Configuración IAM (Permisos de Usuario)

El usuario de AWS que configures en tu PC (tu `aws configure` o `~/.aws/credentials`) necesita permisos para actuar.

### Políticas Necesarias (Policies)
Tu usuario debe tener adjuntadas (Attached) al menos estas políticas:
1.  **AmazonSNSFullAccess** (Para que el Producer pueda publicar).
2.  **AmazonSQSFullAccess** (Para que los Consumers puedan leer y borrar mensajes).
3.  **CloudWatchFullAccess** (Para que los Lambdas envíen métricas de alarmas).

*Sin esto, te dará error de `AccessDenied` o `AuthorizationError`.*

---

## 3. Configuración Local (Tus Scripts)

### A. Base de Datos (MySQL)
*   **Servidor**: Debe estar corriendo en `localhost` puerto `3306`.
*   **Usuario/Pass**: Por defecto en los scripts está `root` / `root`. Si tu MySQL tiene otra contraseña, cámbiala en `DB_CONFIG` en **TODOS** los scripts.
*   **Base de Datos**: Se llama `pc4_clima_events`.
    *   Si tienes dudas, ejecuta `python setup_local_mysql.py` para recrearla.
*   **Tablas**:
    *   `alpinista_data`: Todos los eventos procesados por Alpinista
    *   `dron_data`: Todos los eventos procesados por Dron
    *   `ciclista_data`: Todos los eventos procesados por Ciclista
    *   **`alarmas`**: Solo eventos EXTREMOS de los 3 consumidores (para análisis rápido)

### B. Scripts Python
*   **`SNS_Producer_events.py`**:
    *   Verifica que `TargetArn` coincida con tu SNS de AWS.
    *   Verifica que la `region_name` (ej: 'eu-central-1') sea correcta.
*   **`Lambda_*.py` (Consumidores)**:
    *   Verifica que `QUEUE_URL` coincida con TU cola de AWS.
    *   Verifica que `ALLOWED_EVENTS` coincida con los Strings que envía el Producer (ej: "AirQuality-sensor").

---

## 4. CloudWatch (Monitorización de Alarmas)

Los Lambdas envían automáticamente métricas a CloudWatch cuando detectan **condiciones extremas**.

### Cómo Verificar Métricas
1.  Ve a [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2.  Región: **eu-central-1** (Frankfurt)
3.  Métricas → Todas las métricas → Busca:
    *   `WeatherEvents/Alpinista`
    *   `WeatherEvents/Dron`
    *   `WeatherEvents/Ciclista`
4.  Métrica: `AlertaExtrema` (contador de eventos extremos)

### Condiciones Extremas Detectadas
- **Temperatura**: `EXTREME_COLD`, `EXTREME_HEAT`
- **Viento**: `EXTREME`, `STORM`
- **Calidad del Aire**: `PELIGROSA`, `MUY_INSALUBRE`, `INSALUBRE`
- **Visibilidad**: `CRITICAL`, `VERY_LOW`

---

## 🚑 Resumen de Errores Comunes

| Síntoma | Causa Más Probable | Solución |
| :--- | :--- | :--- |
| **"Ciclista no recibe nada"** | Typo en el Filtro AWS vs Python (`AirQualit` vs `AirQuality`). | Corrige el JSON del Filtro en AWS SNS. |
| **"No se guarda en DB"** | Mirando DB incorrecta o no refrescada. | Refresca DBeaver o revisa nombre de DB. |
| **"QueueDoesNotExist"** | URL de la cola incorrecta en el script. | Copia la URL real desde AWS SQS. |
| **"AccessDenied"** | Falta permiso IAM o Región incorrecta. | Revisa `aws configure` y permisos IAM. |
| **"Recibo mensajes aleatorios"** | Alguien más usa tu misma cola. | Es normal en entornos compartidos. Ignóralo. |
