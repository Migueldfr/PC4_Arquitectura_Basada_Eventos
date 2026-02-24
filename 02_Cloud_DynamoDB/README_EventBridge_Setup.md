# ⚡ EventBridge Scheduler - Producer Automático

Esta guía te ayuda a configurar el Producer en AWS para que se ejecute automáticamente cada minuto sin necesidad de tu PC.

---

## 📋 Paso 1: Crear Lambda Producer

### 1.1 Crear la función

1. Ve a [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. **Create function** → Author from scratch
3. **Configuración:**
   - **Function name:** `WeatherEventProducer`
   - **Runtime:** Python 3.12
   - **Architecture:** x86_64
4. Click **Create function**

### 1.2 Subir código

1. En el editor, **borra** el código de ejemplo
2. **Copia** el contenido de [Lambda_Producer_Cloud.py](./Lambda_Producer_Cloud.py)
3. **⚠️ IMPORTANTE:** Línea 8, cambia el `TOPIC_ARN` por el tuyo:
   ```python
   TOPIC_ARN = 'arn:aws:sns:eu-central-1:accountid:WeatherEvents'
   ```
   
   **¿Dónde encontrar tu ARN?**
   - AWS Console → SNS → Topics → Click en `SNSWeatherEvents` → Copiar el ARN

4. Click **Deploy**

### 1.3 Configurar permisos IAM

1. **Configuration** → **Permissions** → Click en el nombre del **rol**
2. En IAM Console verás una policy ya existente (`AWSLambdaBasicExecutionRole...`) — **NO la toques**, es la que AWS crea automáticamente para que Lambda pueda escribir logs en CloudWatch
3. Click **Add permissions** → **Create inline policy** (esto crea una policy **nueva**, separada de la de logs)
4. Selecciona pestaña **JSON** y pega:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:eu-central-1:TU_ACCOUNT_ID:WeatherEvents"
    }
  ]
}
```
5. Click **Next** → **Name:** `SNSPublishPolicy` → **Create policy**

> ✅ Al final tu rol tendrá **2 policies**: la de logs (auto-generada) + la de SNS (la que acabas de crear)

---

## ⏰ Paso 2: Configurar EventBridge Scheduler

### 2.1 Añadir trigger

1. En tu Lambda `WeatherEventProducer`
2. **Configuration** → **Triggers** → **Add trigger**
3. **Select a source:** EventBridge (CloudWatch Events)
4. **Rule:**
   - Selecciona **Create a new rule**
   - **Rule name:** `WeatherEventSchedule`
   - **Rule description:** `Genera eventos de clima cada 1 minuto`
   - **Rule type:** Schedule expression
   - **Schedule expression:** `rate(1 minute)` O 'rate
5. **Add**

---

## 🧪 Paso 3: Testing

### 3.1 Verificar que funciona

**Espera 1-2 minutos**, luego:

1. Ve a **CloudWatch Logs**:
   - `/aws/lambda/WeatherEventProducer`
2. Deberías ver logs cada minuto:
   ```
   ✅ Evento enviado: temperature-sensor - MessageId: abc123-...
   ```

### 3.2 Verificar que los consumers reciben eventos

1. Ve a CloudWatch Logs:
   - `/aws/lambda/ProcessAlpinista`
   - `/aws/lambda/ProcessDron`
   - `/aws/lambda/ProcessCiclista`
2. Deberías ver logs de eventos procesados

### 3.3 Verificar en DynamoDB

1. DynamoDB Console → `alpinista_events` → Explore table items
2. Deberías ver eventos aparecer automáticamente cada minuto

---

## 🎛️ Ajustar Frecuencia (Opcional)

Si quieres cambiar la frecuencia:

### Cada 5 minutos:
```
rate(5 minutes)
```

### Cada 30 segundos:
```
rate(30 seconds)
```

### Solo en horas laborables (9 AM - 6 PM, Lun-Vie):
```
cron(0 9-18 ? * MON-FRI *)
```

**Para cambiar:**
1. Lambda → Configuration → Triggers → Click en EventBridge
2. Manage in EventBridge
3. Edit → Cambiar Schedule expression → Update

---

## 🛑 Detener el Producer

**Opción 1: Deshabilitar (temporal)**
1. EventBridge → Rules → `WeatherEventSchedule`
2. **Disable**

**Opción 2: Eliminar (permanente)**
1. Lambda → Configuration → Triggers → Remove

---

## 💰 Costos (Free Tier)

| Componente | Free Tier | Real |
|------------|-----------|------|
| Lambda Invocations | 1M/mes | ~43,800/mes (1/min) ✅ |
| Lambda Duration | 400k GB-seg | ~50 GB-seg ✅ |
| SNS Publishes | 1M/mes | ~43,800/mes ✅ |
| **TOTAL** | **$0** | **$0** |

---

## ✅ Checklist

- [ ] Lambda `WeatherEventProducer` creada
- [ ] Código copiado y `TOPIC_ARN` actualizado
- [ ] Permisos SNS configurados
- [ ] EventBridge Trigger añadido (`rate(1 minute)`)
- [ ] Logs verificados en CloudWatch
- [ ] Eventos aparecen en DynamoDB

---

## 🎉 Resultado Final

Ahora tienes un **sistema completamente automático**:

```
EventBridge (cada 1 min)
         ↓
    Lambda Producer
         ↓
       SNS Topic
      /   |   \
   SQS  SQS  SQS
    ↓    ↓    ↓
  Lambda Lambda Lambda
    ↓    ↓    ↓
DynamoDB + CloudWatch
```

**Todo funciona 24/7 sin tu intervención y gratis** 🚀
