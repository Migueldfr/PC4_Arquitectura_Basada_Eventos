# PC4: Consolidación de conocimientos de Arquitecturas Basadas en Eventos

## Objetivo

Este proyecto tiene como objetivo consolidar los conocimientos adquiridos a lo largo del módulo de Arquitecturas Basadas en Eventos (EDA), aplicándolos de forma práctica mediante el diseño e implementación de una arquitectura orientada a eventos con una aplicación realista.

El proyecto se realizará en grupos de 3–4 alumnos, con una dedicación total estimada de 10–15 horas por grupo (aproximadamente 3–4 horas por alumno).

El foco del proyecto no es únicamente que la arquitectura funcione, sino demostrar criterio de diseño, comprensión de los patrones event-driven y la capacidad de justificar decisiones técnicas.

## Contexto general del proyecto

Los sistemas modernos rara vez son monolíticos o puramente síncronos. En su lugar, se basan en:

- eventos
- procesamiento asíncrono
- streaming
- desacoplamiento
- estado derivado

En este proyecto deberéis construir una arquitectura basada en eventos que procese información de forma asíncrona y/o en streaming, mantenga estado derivado y permita extensión y escalado.

## Requisitos generales

### Tecnológicos

El proyecto debe poder resolverse usando una de estas dos opciones (a elegir por el grupo):

#### ✅ Opción A – Cloud (AWS)

- SNS / SQS
- EventBridge
- Lambda
- DynamoDB / DynamoDB Streams
- (Opcional) Kinesis / MSK si la cuenta lo permite

#### Opción B – Open Source

- Kafka / Pulsar
- Consumers / Producers
- Procesamiento (Kafka Streams, Flink, Spark Streaming, etc.)
- Almacenamiento de datos (Redis, PostgreSQL, MongoDB, etc.)

No es obligatorio usar todas las tecnologías, pero sí justificar claramente las elecciones.

## Caso de uso (a elegir o proponer)

Cada grupo debe implementar uno de los siguientes casos de uso, o proponer uno equivalente (previa validación):

### Ejemplos de casos de uso

- Plataforma de eventos de usuarios (clicks, pagos, acciones)
- Procesamiento de eventos IoT (sensores, métricas, alertas)
- Sistema de pedidos (creación, validación, facturación, notificación)
- ✅ Sistema de monitorización / métricas en tiempo casi real

El sistema debe generar eventos continuamente (simulados o reales).

## Requisitos funcionales mínimos

### 1. Generación de eventos

- ✅ Simular una fuente de eventos continua (script, API, productor, etc.)
- ✅ Los eventos deben contener:
 - ✅ identificador
 - ✅ timestamp
 - ✅ algún atributo de negocio (usuario, sensor, pedido, etc.)

### 2. Ingesta y canalización de eventos

- ✅ Usar un canal de eventos (topic, stream, queue, bus)
- ✅ Separar claramente:
 - ✅ productores
 - ✅ consumidores
- ✅ Justificar el tipo de comunicación:
 - ✅ pub/sub
 - ✅ colas
 - streaming

### 3. Procesamiento asíncrono / streaming

- ✅ Procesar eventos en near-real-time
- ✅ Demostrar comprensión de:
 - ✅ orden (SQS FIFO garantiza orden dentro de MessageGroupId)
 - ✅ concurrencia (3 Lambdas procesando en paralelo)
 - ✅ retries (Chaos Monkey + SQS VisibilityTimeout)
 - ✅ idempotencia (ON DUPLICATE KEY UPDATE en MySQL / put_item en DynamoDB)

### 4. Estado y agregados

El sistema debe mantener estado derivado a partir de eventos, por ejemplo:

- ✅ contadores (tabla alarmas: contador de eventos extremos)
- ✅ último valor conocido (DynamoDB guarda último estado por event_id)
- agregados por ventana temporal (opcional - no implementado)

Este estado:

- ✅ no debe recalcularse desde cero
- ✅ debe actualizarse incrementalmente (cada evento actualiza su registro)

### 5. Persistencia

- ✅ Almacenar eventos individuales (todos los eventos en tablas específicas)
- ✅ Almacenar estado agregado (tabla alarmas con eventos críticos)
- ✅ Justificar el modelo de datos elegido:
  - **Local:** MySQL (relacional, familiar, fácil consultas SQL)
  - **Cloud:** DynamoDB (NoSQL, serverless, escalable, Free Tier friendly)

### 6. Manejo de errores

✅ Demostrar qué ocurre cuando un evento falla:

- ✅ **retries:** Chaos Monkey simula fallos (~10%), SQS reintenta automáticamente después de VisibilityTimeout
- ⚠️  **DLQ:** Documentado y explicado, pendiente de configurar en AWS
- ✅ **reintentos:** Implementado y probado (mismo event_id aparece múltiples veces en logs)

✅ Implicaciones explicadas:
- Idempotencia necesaria para evitar duplicados
- At-least-once delivery (puede procesar 2 veces)
- Eventual consistency

## Requisitos no funcionales

- ✅ **Arquitectura desacoplada:** Producer no conoce Consumers, SNS/SQS actúan como intermediarios, cambios en Consumers no afectan Producer
- ✅ **Escalado razonable:** 
  - Lambdas escalan automáticamente (hasta 1000 concurrentes)
  - DynamoDB en modo on-demand escala automáticamente
  - SNS/SQS soportan millones de mensajes/día
- ✅ **Uso responsable de recursos:** Todo dentro de AWS Free Tier ($0/mes estimado)

## Entregables

### 1. README.md

✅ Debe incluir:

- ✅ descripción del caso de uso (sistema de monitorización climática IoT)
- ⚠️  diagrama de arquitectura (pendiente de crear visual profesional)
- ✅ explicación del flujo de eventos (documentado en README_Configuracion_Completa.md)
- ✅ decisiones técnicas (justificadas en implementation_plan.md y walkthrough.md)

### 2. Código fuente

✅ Completo:

- ✅ **Scripts generación eventos:** SNS_Producer_events.py (local) + Lambda_Producer_Cloud.py (AWS)
- ✅ **Consumidores:** 
  - Local: Lambda_Alpinista_Local.py, Lambda_Dron_Local.py, Lambda_Ciclista_Local.py
  - Cloud: Lambda_Alpinista_Cloud.py, Lambda_Dron_Cloud.py, Lambda_Ciclista_Cloud.py
- ✅ **Infraestructura:** create_dynamodb_tables.py, setup_local_mysql.py

### 3. Diagrama de arquitectura

⚠️  Pendiente:

- [ ] diagrama estilo AWS oficial
- ✅ arquitectura textual documentada en múltiples README

### 4. Opcional

✅ **Capturas y logs:**
- ✅ Logs CloudWatch con eventos procesados
- ✅ Screenshots DynamoDB con datos
- ✅ Métricas CloudWatch (AlertaExtrema)
- ✅ Walkthrough.md con evidencia de testing completo