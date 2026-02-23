# PC4 - Arquitectura Basada en Eventos

> **Sistema de monitoreo climático en tiempo real** usando arquitectura event-driven. El proyecto ha evolucionado desde un MVP inicial híbrido (Productor/Consumidores locales + Mensajería AWS) hasta una arquitectura "Full Cloud" implementada 100% con servicios Serverless de AWS.

---

## 🏗️ Evolución de la Arquitectura

### [Fase 1: MVP Local con AWS SNS/SQS y MySQL](./01_Local_MySQL/)
La primera iteración del proyecto se construyó demostrando el patrón **Pub/Sub desacoplado** usando AWS SNS y SQS: 
- El Productor se ejecuta en local y publica eventos meteorológicos (Temperatura, Viento, Calidad del Aire, Visibilidad) en `AWS SNS`.
- `AWS SNS` hace "Fan-out" inteligente distribuyendo eventos a 3 colas `AWS SQS` distintas (Alpinista, Ciclista, Dron) filtrando exhaustivamente por `eventType`.
- Los Consumidores son hilos de un único script en Python ejecutado en local que hacen polling continuo sobre las colas SQS y persisten todo en una base de datos relacional **MySQL Local**.

👉 **[Ir a carpeta del MVP Local (01_Local_MySQL)](./01_Local_MySQL/)**

### [Fase 2: Arquitectura "Full Cloud" con Lambdas y DynamoDB](./02_Cloud_DynamoDB/)
La evolución definitiva del sistema donde **toda la infraestructura y ejecución** pasa a la nube AWS (Serverless Event-Driven Puro):
- Integración de **EventBridge Scheduler** para ejecutar a un Productor automático en `AWS Lambda` periódicamente (rate de 1 minuto).
- Implementación de **Event-Driven Serverless** con 3 consumidores paralelos en `AWS Lambda` que son disparados directamente desde `AWS SQS` sin necesidad de long-polling o esperas activas.
- Persistencia de datos ultrarrápida (NoSQL) utilizando **Amazon DynamoDB** (una tabla independiente por consumidor y una tabla consolidada para registro de alarmas).
- Telemetría avanzada y Notificaciones: Alarmas por métricas generadas con **Amazon CloudWatch** y envío automático de notificaciones por **Email a través de AWS SNS** cuando se detectan eventos climáticos críticos.
- Tolerancia a fallos utilizando **Dead Letter Queues (DLQ)** para manejar eventos con errores sin pérdida de información (máximo 3 reintentos).

👉 **[Ver Guía Maestra de Despliegue en Cloud (02_Cloud_DynamoDB/README_Deployment.md)](./02_Cloud_DynamoDB/README_Deployment.md)**

👉 **[Ver Diagrama Visual de Arquitectura Cloud](./02_Cloud_DynamoDB/Arquitectura_PC4_Cloud.drawio)**

---

## 📁 Estructura del Repositorio

```text
PC4_Arquitectura_Basada_Eventos/
│
├── 01_Local_MySQL/                    # Fase 1: MVP. Productor y consumidor Python (local) con MySQL.
│   ├── SNS_Producer_events.py
│   ├── Consumidor_Multitarea_MySQL.py
│   ├── setup_local_mysql.py
│   └── ...
│
├── 02_Cloud_DynamoDB/                 # Fase 2: "Full Cloud". Archivos arquitectura Serverless.
│   ├── Lambda_Producer_Cloud.py
│   ├── Lambda_Alpinista_Cloud.py
│   ├── Lambda_Ciclista_Cloud.py
│   ├── Lambda_Dron_Cloud.py
│   ├── create_dynamodb_tables.py
│   ├── Arquitectura_PC4_Cloud.drawio  # Diagrama completo editado en draw.io
│   ├── README_Deployment.md           # ✨ GUÍA COMPLETA STEP-BY-STEP (Infra + Testing) ✨
│   └── README_EventBridge_Setup.md
│
├── .gitignore                         # Exclusión de archivos (VENV, .env, OS files)
├── Guia_Maestra_Arquitectura.md       # Documento técnico sobre los patrones AWS usados
└── enunciado_pc4.md                   # Requerimientos originales del TFM/Práctica
```

---

## 👨‍💻 Autor

**Miguel** - Data Engineering MBIT 2025  
Proyecto: PC4 - Arquitecturas Basadas en Eventos
