# 🚀 Despliegue en AWS Cloud (DynamoDB + Lambda)

Esta carpeta contiene todo lo necesario para ejecutar el sistema de eventos en **AWS Cloud** usando **DynamoDB** y **Lambda**.

---

## 📋 Requisitos Previos

1. ✅ Cuenta AWS activa
2. ✅ AWS CLI configurado (`aws configure`)
3. ✅ Permisos IAM necesarios:
   - `DynamoDBFullAccess`
   - `AWSLambda_FullAccess`
   - `AmazonSQSFullAccess`
   - `CloudWatchFullAccess`

---

## 📧 Paso 0: Configurar Notificaciones por Email (SNS Alerts)

Cuando se detecta una condición meteorológica extrema (EXTREME_COLD, STORM, CRITICAL, etc.), el sistema te enviará un **email automático** con los detalles de la alerta.

### 0.1 Crear SNS Topic para Alertas

1. Ve a [SNS Console](https://console.aws.amazon.com/sns/)
2. **Topics** → **Create topic**
3. **Configuración:**
   - **Type:** Standard
   - **Name:** `WeatherAlertNotifications`
   - Deja todo lo demás por defecto
4. Click **Create topic**
5. ⚠️ **COPIA el ARN** del topic (lo necesitarás luego), será algo como:
   ```
   arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications
   ```

### 0.2 Suscribir tu Email

1. Dentro del topic `WeatherAlertNotifications`, click **Create subscription**
2. **Configuración:**
   - **Protocol:** Email
   - **Endpoint:** `tu-correo@ejemplo.com` ← ⚠️ **Pon tu email real aquí**
3. Click **Create subscription**
4. 📬 **Ve a tu bandeja de entrada** y busca un email de `AWS Notifications`
5. Click en **Confirm subscription** en el email
6. Vuelve a la consola SNS y verifica que el Status dice **Confirmed** ✅

> **⚠️ IMPORTANTE:** Si no confirmas la suscripción desde tu correo, NO recibirás alertas. Revisa también la carpeta de SPAM.

### 0.3 Verificación rápida (Opcional)

Para probar que funciona **antes** de configurar las Lambdas:

1. En el topic `WeatherAlertNotifications`, click **Publish message**
2. **Subject:** `Test de alerta`
3. **Message body:** `Si recibes esto, las alertas funcionan correctamente`
4. Click **Publish message**
5. Comprueba tu email 📧

### 0.4 Actualizar el Código de las 3 Lambdas

Para **cada Lambda** (`ProcessAlpinista`, `ProcessDron`, `ProcessCiclista`):

1. Ve a [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Click en la función (ej: `ProcessAlpinista`)
3. Pestaña **Code** → **Borra** todo el código actual
4. **Copia y pega** el contenido actualizado del archivo correspondiente:
   - ProcessAlpinista → [Lambda_Alpinista_Cloud.py](./Lambda_Alpinista_Cloud.py)
   - ProcessCiclista → [Lambda_Ciclista_Cloud.py](./Lambda_Ciclista_Cloud.py)
   - ProcessDron → [Lambda_Dron_Cloud.py](./Lambda_Dron_Cloud.py)
5. Click **Deploy** ✅

### 0.5 Añadir Variable de Entorno `ALERT_TOPIC_ARN`

Para **cada Lambda**:

1. Pestaña **Configuration** → **Environment variables** → **Edit**
2. Click **Add environment variable**
3. Añadir:
   ```
   Key:   ALERT_TOPIC_ARN
   Value: arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications
   ```
   > ⚠️ Pega el ARN exacto que copiaste en el paso 0.1
4. Click **Save**

### 0.6 Actualizar Permisos IAM (sns:Publish)

Para **cada Lambda**:

1. Pestaña **Configuration** → **Permissions** → Click en el nombre del **rol**
2. En IAM Console, busca la **inline policy** existente (ej: `LambdaDynamoDBCloudWatchPolicy`)
3. Click **Edit** → Pestaña **JSON**
4. Dentro del array `"Statement"`, **añade este bloque** después del último `}` (no olvides la coma):
   ```json
   ,
   {
     "Effect": "Allow",
     "Action": "sns:Publish",
     "Resource": "arn:aws:sns:eu-central-1:*:WeatherAlertNotifications"
   }
   ```
5. Click **Review policy** → **Save changes**

> 💡 Si prefieres crear una nueva inline policy en vez de editar la existente, también funciona. Lo importante es que la Lambda tenga permiso `sns:Publish` sobre el topic `WeatherAlertNotifications`.

### 0.7 Probar que Llegan los Emails

1. Ejecuta el Producer:
   ```bash
   python SNS_Producer_events.py
   ```
2. Espera a que se genere un evento extremo (EXTREME_COLD, STORM, CRITICAL, etc.)
3. Revisa tu correo — deberías recibir algo como:
   ```
   Asunto: 🚨 ALERTA EXTREMA [Alpinista]: EXTREME_COLD

   ⚠️ ALERTA METEOROLÓGICA EXTREMA
   ========================================
   Consumidor: Alpinista
   Tipo Sensor: temperature-sensor
   Estado: EXTREME_COLD
   Valor: -55.3 Cº
   Sensor ID: temp4521
   ========================================
   ```
4. Verifica en **CloudWatch Logs** que aparece: `📧 [EMAIL] Notificación enviada: EXTREME_COLD`

---

## 🗄️ Paso 1: Crear Tablas DynamoDB

Ejecuta el script automatizado:

```bash
python create_dynamodb_tables.py
```

**Esto creará 4 tablas:**
- `alpinista_events`: Eventos de temperatura y viento
- `dron_events`: Eventos de viento y visibilidad
- `ciclista_events`: Eventos de calidad del aire y visibilidad
- `weather_alarmas`: Solo eventos extremos de los 3 consumidores

**Verificar en AWS Console:**
1. Ve a [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Región: **eu-central-1** (Frankfurt)
3. Deberías ver las 4 tablas con estado `ACTIVE`

---

## ⚡ Paso 2: Crear Funciones Lambda

### Opción A: AWS Console (Recomendado para empezar)

#### 2.1 Crear Lambda "ProcessAlpinista"

1. Ve a [Lambda Console](https://console.aws.amazon.com/lambda/)
2. **Create function** → Author from scratch
3. **Configuración:**
   - **Function name:** `ProcessAlpinista`
   - **Runtime:** Python 3.12
   - **Architecture:** x86_64
   - **Permissions:** Create a new role (lo configuraremos después)
4. Click **Create function**

#### 2.2 Subir Código

1. En la pestaña **Code**, elimina el código de ejemplo
2. Copia y pega el contenido completo de [Lambda_Alpinista_Cloud.py](./Lambda_Alpinista_Cloud.py)
3. Click **Deploy**

#### 2.3 Configurar Variables de Entorno

1. Pestaña **Configuration** → **Environment variables** → **Edit**
2. Añadir:
   ```
   TABLE_NAME = alpinista_events
   ALARMAS_TABLE = weather_alarmas
   ALLOWED_EVENTS = temperature-sensor,wind-sensor
   CONSUMIDOR = Alpinista
   ALERT_TOPIC_ARN = arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications
   ```
   > ⚠️ Sustituye `TU_ACCOUNT_ID` por tu ID de cuenta AWS, o pega directamente el ARN que copiaste en el Paso 0.1
3. **Save**

#### 2.4 Ajustar Configuración General

1. **Configuration** → **General configuration** → **Edit**
2. **Timeout:** 30 segundos
3. **Memory:** 256 MB
4. **Save**

#### 2.5 Añadir Trigger SQS

1. Pestaña **Configuration** → **Triggers** → **Add trigger**
2. **Select a source:** SQS
3. **SQS queue:** Selecciona `weather_alpinista`
4. **Batch size:** 10
5. **Add**

#### 2.6 Configurar Permisos IAM

1. **Configuration** → **Permissions** → Click en el rol
2. En IAM Console, **Add permissions** → **Attach policies**
3. Buscar y añadir:
   - `AWSLambdaSQSQueueExecutionRole` (si no está ya)
4. **Add permissions** → **Create inline policy**
5. Pegar este JSON:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "dynamodb:PutItem",
           "dynamodb:GetItem"
         ],
         "Resource": [
           "arn:aws:dynamodb:eu-central-1:*:table/alpinista_events",
           "arn:aws:dynamodb:eu-central-1:*:table/weather_alarmas"
         ]
       },
       {
         "Effect": "Allow",
         "Action": "cloudwatch:PutMetricData",
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": "sns:Publish",
         "Resource": "arn:aws:sns:eu-central-1:*:WeatherAlertNotifications"
       }
     ]
   }
   ```
6. **Review policy** → Name: `LambdaDynamoDBCloudWatchSNSPolicy` → **Create policy**

---

### Repetir para ProcessDron y ProcessCiclista

**ProcessDron:**
- Código: [Lambda_Dron_Cloud.py](./Lambda_Dron_Cloud.py)
- Variables de entorno:
  ```
  TABLE_NAME = dron_events
  ALARMAS_TABLE = weather_alarmas
  ALLOWED_EVENTS = wind-sensor,visibility-sensor
  CONSUMIDOR = Dron
  ALERT_TOPIC_ARN = arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications
  ```
- Trigger: `weather_dron` queue
- Permisos: Cambiar `alpinista_events` → `dron_events` en el policy

**ProcessCiclista:**
- Código: [Lambda_Ciclista_Cloud.py](./Lambda_Ciclista_Cloud.py)
- Variables de entorno:
  ```
  TABLE_NAME = ciclista_events
  ALARMAS_TABLE = weather_alarmas
  ALLOWED_EVENTS = AirQuality-sensor,visibility-sensor
  CONSUMIDOR = Ciclista
  ALERT_TOPIC_ARN = arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications
  ```
- Trigger: `weather_ciclista` queue
- Permisos: Cambiar `alpinista_events` → `ciclista_events` en el policy

> **💡 TIP:** Las 3 Lambdas publican al **mismo** topic `WeatherAlertNotifications`. Así recibes todas las alertas en un solo email, independientemente de qué consumidor la detecte.

---

## 🧪 Paso 3: Testing

### 3.1 Ejecutar Producer (Local)

Desde la carpeta raíz del proyecto:

```bash
cd ../01_Local_MySQL
python SNS_Producer_events.py
```

El producer **no cambia**, sigue enviando eventos a SNS/SQS.

### 3.2 Verificar CloudWatch Logs

1. Ve a [CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home?region=eu-central-1#logsV2:log-groups)
2. Busca:
   - `/aws/lambda/ProcessAlpinista`
   - `/aws/lambda/ProcessDron`
   - `/aws/lambda/ProcessCiclista`
3. Deberías ver logs como:
   ```
   📩 Recibido [abc12345]: temperature-sensor
   🚨 [CLOUDWATCH] Alarma enviada: temperature-sensor - EXTREME_COLD
   💾 [DYNAMODB] Alarma guardada en tabla 'weather_alarmas'
   📧 [EMAIL] Notificación enviada: EXTREME_COLD
   ✅ [Alpinista] Guardado: temperature-sensor - abc12345
   ```

### 3.3 Consultar DynamoDB

1. Ve a [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Selecciona `alpinista_events` → **Explore table items**
3. Deberías ver eventos guardados
4. Haz lo mismo con `weather_alarmas` (solo extremos)

### 3.4 Verificar CloudWatch Metrics

1. [CloudWatch Metrics Console](https://console.aws.amazon.com/cloudwatch/home?region=eu-central-1#metricsV2:)
2. Buscar namespaces:
   - `WeatherEvents/Alpinista`
   - `WeatherEvents/Dron`
   - `WeatherEvents/Ciclista`
3. Métrica: `AlertaExtrema`

### 3.5 Verificar Email de Alertas

1. Ejecuta el Producer y espera a que se genere un evento extremo
2. Revisa tu correo electrónico — deberías recibir algo así:
   ```
   Asunto: 🚨 ALERTA EXTREMA [Alpinista]: EXTREME_COLD

   ⚠️ ALERTA METEOROLÓGICA EXTREMA
   ========================================
   Consumidor: Alpinista
   Tipo Sensor: temperature-sensor
   Estado: EXTREME_COLD
   Valor: -55.3 Cº
   Sensor ID: temp4521
   Timestamp: 2026-02-16T22:45:00
   Event ID: 87231
   ========================================
   Sistema de Monitorización Climática IoT - PC4
   ```

---

## 🔧 Troubleshooting

### Error: "User is not authorized to perform: dynamodb:PutItem"
**Solución:** Revisa los permisos IAM del rol de Lambda. Asegúrate de que el ARN de la tabla es correcto.

### No aparecen logs en CloudWatch
**Solución:** Verifica que el trigger SQS está habilitado. Ve a Lambda → Configuration → Triggers.

### Eventos no llegan a DynamoDB
**Solución:** 
1. Verifica que el Producer está corriendo
2. Verifica que las SQS queues tienen mensajes (AWS Console → SQS)
3. Revisa CloudWatch Logs para errores

### Chaos Monkey falla constantemente
**Solución:** Puedes comentar la línea `simular_fallo_aleatorio()` en las Lambdas temporalmente.

### No recibo emails de alerta
**Solución:**
1. Verifica que confirmaste la suscripción SNS (revisa SPAM)
2. Comprueba que `ALERT_TOPIC_ARN` está configurado en las variables de entorno de Lambda
3. Revisa CloudWatch Logs — debe aparecer `📧 [EMAIL] Notificación enviada`
4. Si ves `⚠️ Error enviando email`, revisa los permisos IAM (necesita `sns:Publish`)

---

## 📊 Costos Estimados

Todos los servicios están en **Free Tier**:

| Servicio | Free Tier | Estimado |
|----------|-----------|----------|
| DynamoDB | 25 GB + 25 WCU/RCU | $0 |
| Lambda | 1M invocaciones/mes | $0 |
| CloudWatch Logs | 5 GB | $0 |
| SQS | 1M requests | $0 |
| SNS (Email) | 1,000 notificaciones/mes | $0 |

**Total:** ~$0/mes

---

## 🎯 Diferencias vs. Local (MySQL)

| Aspecto | Local | Cloud |
|---------|-------|-------|
| Base de Datos | MySQL local | DynamoDB |
| Ejecución | Scripts Python manuales | AWS Lambda automático |
| Escalabilidad | Limitada | Ilimitada (auto-scaling) |
| Costo | $0 (local) | $0 (Free Tier) |
| Disponibilidad | Solo cuando ejecutas | 24/7 automático |
| Alertas Email | ❌ No | ✅ Sí (SNS → Email) |

---

## 🏗️ Arquitectura Final (Cloud)

```
EventBridge (cada 1 min)
         ↓
    Lambda Producer ──→ SNS WeatherEvents
                          /    |    \
                       SQS   SQS   SQS
                        ↓      ↓      ↓
                    Lambda  Lambda  Lambda
                    Alpin.  Cicli.  Dron
                        ↓      ↓      ↓
                    ┌──────────────────────┐
                    │   DynamoDB (4 tablas) │
                    │   + CloudWatch Metrics│
                    └──────────────────────┘
                              ↓
                    Si evento EXTREMO → SNS Alert Topic → 📧 Email
```

---

## ✅ Checklist de Despliegue

- [ ] **SNS Alert Topic** `WeatherAlertNotifications` creado
- [ ] **Email suscrito** y confirmado
- [ ] Tablas DynamoDB creadas (`python create_dynamodb_tables.py`)
- [ ] Lambda ProcessAlpinista creada y configurada (con `ALERT_TOPIC_ARN`)
- [ ] Lambda ProcessDron creada y configurada (con `ALERT_TOPIC_ARN`)
- [ ] Lambda ProcessCiclista creada y configurada (con `ALERT_TOPIC_ARN`)
- [ ] Permisos IAM configurados (DynamoDB + CloudWatch + **SNS**)
- [ ] Triggers SQS añadidos
- [ ] Producer ejecutado y eventos generados
- [ ] Logs verificados en CloudWatch
- [ ] Datos verificados en DynamoDB
- [ ] Métricas verificadas en CloudWatch
- [ ] **📧 Email de alerta recibido y verificado**

---

## � Paso 4: Configurar Dead Letter Queues (DLQ)

Cuando un mensaje falla demasiadas veces (por ejemplo, por el Chaos Monkey), en vez de perderlo, lo enviamos a una **cola de mensajes muertos** para revisión manual.

### 4.1 Crear 3 Colas DLQ

1. Ve a [SQS Console](https://console.aws.amazon.com/sqs/)
2. **Create queue** con la siguiente configuración:

| Nombre de la DLQ | Cola principal asociada |
|-------------------|------------------------|
| `weather_alpinista_dlq` | `weather_alpinista` |
| `weather_ciclista_dlq` | `weather_ciclista` |
| `weather_dron_dlq` | `weather_dron` |

Para **cada DLQ**:
1. **Type:** Standard
2. **Name:** (uno de los nombres de arriba)
3. **Configuration:**
   - **Visibility timeout:** 30 segundos
   - **Message retention period:** 14 días (máximo, para poder investigar)
   - **Receive message wait time:** 0
4. Deja todo lo demás por defecto
5. Click **Create queue**

### 4.2 Asociar DLQ a las Colas Principales

Para **cada cola principal** (`weather_alpinista`, `weather_ciclista`, `weather_dron`):

1. En SQS Console, click en la cola principal (ej: `weather_alpinista`)
2. **Edit** → Sección **Dead-letter queue**
3. **Enabled:** ✅ Sí
4. **Choose queue:** Selecciona la DLQ correspondiente (ej: `weather_alpinista_dlq`)
5. **Maximum receives:** `3`
   > Esto significa: si un mensaje falla 3 veces, se mueve automáticamente a la DLQ
6. Click **Save**

### 4.3 Verificar que la DLQ Funciona

1. Asegúrate de que el **Chaos Monkey** está activo en las Lambdas (no comentado)
2. Ejecuta el Producer y genera varios eventos
3. En la consola SQS, verifica:
   - **Cola principal** → Messages Available debería ser ~0 (se procesan rápido)
   - **Cola DLQ** → Si hubo fallos repetidos, deberías ver mensajes aquí
4. Para **ver los mensajes** en la DLQ:
   - Click en la DLQ → **Send and receive messages** → **Poll for messages**
   - Podrás ver el contenido del evento que falló

### 4.4 ¿Qué hacer con los mensajes en la DLQ?

**Opción A: Re-procesar** (redrive)
1. En la DLQ → **Start DLQ redrive**
2. Selecciona la cola de destino original
3. Los mensajes vuelven a intentar procesarse

**Opción B: Investigar y borrar**
1. Lee los mensajes para entender por qué fallaron
2. Si fue un fallo temporal (Chaos Monkey), haz redrive
3. Si fue un error de datos, borra los mensajes

---

## � Paso 5: Configurar CloudWatch Alarmas → Email Automático

Además de los emails directos que envían las Lambdas, puedes crear **CloudWatch Alarms** que monitorizan la métrica `AlertaExtrema` y te avisan si hay demasiadas alertas en poco tiempo (ej: "más de 5 alertas en 5 minutos" = posible emergencia).

### 5.1 Crear la Alarma para Alpinista

1. Ve a [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/home?region=eu-central-1)
2. **Alarms** → **All alarms** → **Create alarm**
3. **Select metric:**
   - Click **Custom Namespaces** → `WeatherEvents/Alpinista`
   - Selecciona dimensión `EventType, Status`
   - Marca la métrica `AlertaExtrema`
   - Click **Select metric**
4. **Metric configuration:**
   - **Statistic:** Sum
   - **Period:** 5 minutes
5. **Conditions:**
   - **Threshold type:** Static
   - **Whenever AlertaExtrema is:** Greater than
   - **Threshold value:** `5`
   > Esto significa: si hay más de 5 alertas extremas en 5 minutos → alarma
6. Click **Next**

### 5.2 Configurar la Notificación

1. **Notification:**
   - **Alarm state trigger:** In alarm
   - **Select an SNS topic:** Select an existing SNS topic
   - **Send a notification to:** `WeatherAlertNotifications` (el mismo topic del Paso 0)
   > ⚠️ Si no aparece, escribe el ARN completo: `arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherAlertNotifications`
2. Click **Next**
3. **Alarm name:** `AlertaExtrema-Alpinista-5min`
4. **Description:** `Más de 5 alertas extremas del Alpinista en 5 minutos`
5. Click **Next** → **Create alarm**

### 5.3 Repetir para Ciclista y Dron

Crea 2 alarmas más con la misma configuración, cambiando:

| Alarma | Namespace | Nombre |
|--------|-----------|--------|
| Ciclista | `WeatherEvents/Ciclista` | `AlertaExtrema-Ciclista-5min` |
| Dron | `WeatherEvents/Dron` | `AlertaExtrema-Dron-5min` |

### 5.4 Verificar que Funcionan

1. En CloudWatch → **Alarms**, deberías ver 3 alarmas en estado `OK` o `Insufficient data`
2. Cuando el Producer genere suficientes eventos extremos, el estado cambiará a `In alarm`
3. Recibirás un email con el asunto: `ALARM: "AlertaExtrema-Alpinista-5min" in EU (Frankfurt)`

### 5.5 ¿Cuándo se activa cada tipo de email?

| Tipo de Email | Cuándo se envía | Ejemplo |
|---------------|----------------|---------|
| **Email directo** (Lambda → SNS) | Cada vez que se detecta UN evento extremo | `🚨 ALERTA EXTREMA [Alpinista]: EXTREME_COLD` |
| **CloudWatch Alarm** | Cuando hay MUCHOS eventos extremos en poco tiempo | `ALARM: AlertaExtrema-Alpinista-5min` |

> 💡 Son complementarios: el email directo te informa de cada evento, la alarma te avisa de una posible **emergencia sostenida**.

---

## ⏰ Paso 6: Configurar EventBridge — Producer Automático (Sin PC)

Con EventBridge, el Producer se ejecuta automáticamente cada minuto **en la nube**, sin necesidad de tener tu PC encendido.

### 6.1 Crear Lambda Producer

1. Ve a [Lambda Console](https://console.aws.amazon.com/lambda/)
2. **Create function** → Author from scratch
3. **Configuración:**
   - **Function name:** `WeatherEventProducer`
   - **Runtime:** Python 3.12
   - **Architecture:** x86_64
4. Click **Create function**

### 6.2 Subir Código

1. En el editor, **borra** el código de ejemplo
2. **Copia y pega** el contenido de [Lambda_Producer_Cloud.py](./Lambda_Producer_Cloud.py)
3. **⚠️ IMPORTANTE:** Verifica que el `TOPIC_ARN` en la línea 7 tiene tu ARN correcto:
   ```python
   TOPIC_ARN = 'arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherEvents'
   ```
   > Puedes encontrar tu ARN en: AWS Console → SNS → Topics → `SNSWeatherEvents`
4. Click **Deploy**

### 6.3 Configurar Permisos IAM

1. Pestaña **Configuration** → **Permissions** → Click en el rol
2. En IAM Console → **Add permissions** → **Create inline policy** → Pestaña **JSON**
3. Pegar:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "sns:Publish",
         "Resource": "arn:aws:sns:eu-central-1:*:SNSWeatherEvents"
       }
     ]
   }
   ```
4. **Name:** `SNSPublishPolicy` → **Create policy**

### 6.4 Añadir Trigger EventBridge

1. En tu Lambda `WeatherEventProducer`
2. Pestaña **Configuration** → **Triggers** → **Add trigger**
3. **Select a source:** EventBridge (CloudWatch Events)
4. **Rule:** Create a new rule
   - **Rule name:** `WeatherEventSchedule`
   - **Rule description:** `Genera eventos de clima cada 1 minuto`
   - **Rule type:** Schedule expression
   - **Schedule expression:** `rate(1 minute)`
5. Click **Add**

### 6.5 Verificar que Funciona

1. **Espera 1-2 minutos**
2. Ve a CloudWatch Logs → `/aws/lambda/WeatherEventProducer`
3. Deberías ver cada minuto:
   ```
   ✅ Evento enviado: temperature-sensor - MessageId: abc123-...
   ```
4. Verifica que las Lambdas consumidoras también procesan:
   - `/aws/lambda/ProcessAlpinista`
   - `/aws/lambda/ProcessCiclista`
   - `/aws/lambda/ProcessDron`

### 6.6 Detener / Reanudar el Producer

- **Pausar (temporal):** EventBridge → Rules → `WeatherEventSchedule` → **Disable**
- **Reanudar:** EventBridge → Rules → `WeatherEventSchedule` → **Enable**
- **Eliminar (permanente):** Lambda → Configuration → Triggers → **Remove**

> ⚠️ Recuerda desactivar el EventBridge cuando no estés haciendo demos para no gastar invocaciones innecesarias (aunque sigue siendo Free Tier).

---

## 🎬 Paso 7: Testing End-to-End — Demo Completa

Para probar **toda la arquitectura de extremo a extremo** y hacer una demo con tus compañeros.

### 7.1 Verificar que Todo Está Activo

Antes de la demo, comprueba:

| Componente | Dónde verificar | Estado esperado |
|------------|----------------|-----------------|
| SNS Topic `SNSWeatherEvents` | SNS Console → Topics | Activo |
| SNS Topic `WeatherAlertNotifications` | SNS Console → Topics | Activo + Email Confirmed |
| 3 Colas SQS | SQS Console | Activas, 0 mensajes |
| 3 Lambdas Consumer | Lambda Console | Código deployado, triggers activos |
| Lambda Producer | Lambda Console | Código deployado |
| EventBridge Rule | EventBridge → Rules | Enabled |
| 4 Tablas DynamoDB | DynamoDB Console | ACTIVE |

### 7.2 Activar la Arquitectura

1. Ve a EventBridge → Rules → `WeatherEventSchedule` → **Enable** (si estaba desactivado)
2. ¡Listo! Cada minuto se genera un evento automáticamente

### 7.3 Qué Enseñar en la Demo (Guión ~5 min)

| Minuto | Qué enseñas | Dónde |
|--------|-------------|-------|
| 0:00 | "Esta es la arquitectura" — explicar diagrama | README / pizarra |
| 0:30 | "El EventBridge ejecuta el Producer cada minuto" | EventBridge Console |
| 1:00 | "Los eventos llegan a SNS y se filtran a 3 colas" | SNS Console → Monitoring |
| 2:00 | "Las Lambdas procesan automáticamente" | CloudWatch Logs (mostrar logs en vivo) |
| 3:00 | "Los datos se guardan en DynamoDB" | DynamoDB Console → Explore items |
| 3:30 | "Si hay alerta extrema, me llega un email" | Tu correo (mostrar email recibido) |
| 4:00 | "El Chaos Monkey simula fallos y SQS reintenta" | CloudWatch Logs (buscar `💥 CHAOS MONKEY`) |
| 4:30 | "Preguntas?" | — |

### 7.4 Forzar un Evento Extremo (Para la Demo en Vivo)

Si quieres **garantizar** que se vea un email en la demo:

1. Ve a Lambda → `ProcessAlpinista` → Pestaña **Test**
2. Crea un evento de test con este JSON:
   ```json
   {
     "Records": [
       {
         "body": "{\"Message\": \"{\\\"eventId\\\": \\\"99999\\\", \\\"eventType\\\": \\\"temperature-sensor\\\", \\\"timestamp\\\": \\\"2026-02-16T23:30:00\\\", \\\"data\\\": {\\\"sensorId\\\": \\\"temp1234\\\", \\\"value\\\": -55.3, \\\"unit\\\": \\\"Cº\\\", \\\"status\\\": \\\"EXTREME_COLD\\\"}}\"}"
       }
     ]
   }
   ```
3. Click **Test** → Verás el email llegar al momento 📧

### 7.5 Después de la Demo

1. Ve a EventBridge → Rules → `WeatherEventSchedule` → **Disable**
2. Así no se siguen generando eventos innecesarios

---

## 🚀 Próximos Pasos (Opcional)

1. **CI/CD:** Deployment automático con GitHub Actions o AWS SAM
2. **API Gateway:** Endpoint REST para enviar eventos manualmente
3. **Dashboard CloudWatch:** Panel visual con métricas en tiempo real
