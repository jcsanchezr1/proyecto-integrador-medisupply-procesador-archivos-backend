# MediSupply Video Processor Backend

Sistema procesador de videos de visitas backend para el proyecto integrador MediSupply.

## Arquitectura

Estructura básica preparada para escalar:

```
├── app/
│   ├── config/          # Configuración
│   ├── controllers/     # Controladores REST
│   │   └── health_controller.py  # Healthcheck funcional
│   ├── services/        # Lógica de negocio (estructura)
│   ├── repositories/    # Acceso a datos (estructura)
│   ├── models/          # Modelos de datos (estructura)
│   ├── exceptions/      # Excepciones (estructura)
│   └── utils/           # Utilidades (estructura)
├── tests/               # Tests (estructura)
├── app.py              # Punto de entrada
├── requirements.txt    # Mismas versiones del proyecto sample
├── Dockerfile         # Containerización
├── docker-compose.yml # Orquestación
└── README.md          # Documentación
```

## Características

- **Procesamiento de Videos**: Procesa videos de visitas de clientes agregando logo corporativo en los primeros 3 segundos
- **Pub/Sub Integration**: Recibe eventos de Google Cloud Pub/Sub para procesamiento asíncrono
- **Cloud Storage**: Integración con Google Cloud Storage para almacenamiento de videos
- **Health Check**: Endpoint de monitoreo del servicio en `/video-processor/ping`
- **Docker**: Containerización para local y Cloud Run
- **Flask**: Framework web minimalista
- **CORS**: Habilitado para desarrollo

## Tecnologías

- Python 3.9
- Flask 3.0.3
- MoviePy 1.0.3 (procesamiento de video)
- Google Cloud Storage
- Google Cloud Pub/Sub
- PostgreSQL (base de datos)
- SQLAlchemy 2.0.34
- Gunicorn 21.2.0
- Docker

## Instalación

### Desarrollo Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

### Con Docker

1. Construir y ejecutar:
   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en `http://localhost:8080`

## Endpoints

### Health Check
- `GET /files-procesor/ping` - Retorna "pong" para verificar el estado del servicio

### Video Processing
- `POST /files-procesor/video` - Endpoint para recibir eventos de Pub/Sub para procesamiento de videos

#### Formato del evento Pub/Sub

```json
{
  "message": {
    "data": "base64_encoded_data",
    "messageId": "message_id",
    "publishTime": "timestamp"
  },
  "subscription": "subscription_name"
}
```

El `data` decodificado debe contener:

```json
{
  "scheduled_visit_client_id": 1234,
  "event_type": "video_processing",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Procesamiento de Videos

El sistema procesa videos de visitas de clientes siguiendo estos pasos:

1. **Recepción del evento**: Llega un evento de Pub/Sub con el ID del cliente en visita
2. **Descarga del video**: Se descarga el video original desde Cloud Storage
3. **Procesamiento**: Se agrega el logo de MediSupply (`resources/logoMedisupply.png`) en los primeros 3 segundos
4. **Subida del video procesado**: Se sube el video procesado con el sufijo `_processed.mp4`
5. **Actualización de la BD**: Se actualiza el registro en `scheduled_visit_clients` con:
   - `file_status`: "Procesado"
   - `filename_processed`: Nombre del archivo procesado
   - `filename_url_processed`: URL firmada del archivo procesado

## Cloud Run

Para desplegar en Google Cloud Run:

1. Construir imagen:
   ```bash
   docker build -t gcr.io/PROJECT_ID/medisupply-video-processor .
   ```

2. Subir imagen:
   ```bash
   docker push gcr.io/PROJECT_ID/medisupply-video-processor
   ```

3. Desplegar:
   ```bash
   gcloud run deploy medisupply-video-processor \
     --image gcr.io/PROJECT_ID/medisupply-video-processor \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --timeout 600
   ```

**Nota**: Se recomienda aumentar la memoria y el timeout para el procesamiento de videos.

## Variables de Entorno

### Generales
- `FLASK_ENV`: Entorno (development/production)
- `PORT`: Puerto del servicio (default: 8080)
- `HOST`: Host del servicio (default: 0.0.0.0)
- `DEBUG`: Modo debug (default: True)
- `SECRET_KEY`: Clave secreta para Flask

### Google Cloud Platform
- `GCP_PROJECT_ID`: ID del proyecto de GCP
- `GOOGLE_APPLICATION_CREDENTIALS`: Ruta a las credenciales de servicio

### Google Cloud Storage
- `BUCKET_NAME`: Nombre del bucket de GCS (default: medisupply-bucket)
- `BUCKET_FOLDER`: Carpeta en el bucket para videos originales y procesados (default: sales-plan)
- `SIGNING_SERVICE_ACCOUNT_EMAIL`: Email del service account para firmar URLs
- `MAX_CONTENT_LENGTH`: Tamaño máximo de archivo (default: 500MB)


### Base de Datos
- `DATABASE_URL`: URL de conexión a PostgreSQL (default: postgresql://postgres:postgres@localhost:5432/medisupply)

## Testing

### Ejecutar Tests

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con información detallada
pytest -v

# Ejecutar pruebas específicas
pytest tests/test_health_controller.py

# Ejecutar pruebas de un módulo específico
pytest tests/test_video_processor_service.py -v
```

### Ejecutar con Coverage

```bash
# Ejecutar pruebas con coverage
pytest --cov=app --cov-report=term-missing

# Generar reporte HTML de coverage
pytest --cov=app --cov-report=html

# Verificar coverage mínimo del 95%
pytest --cov=app --cov-fail-under=95

# Ejecutar solo tests que fallan
pytest --lf
```
