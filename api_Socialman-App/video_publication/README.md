# SocialMan Video Publishing Service

Microservicio profesional para la publicación automatizada de videos en múltiples plataformas de redes sociales (Instagram, TikTok, X/Twitter, Facebook) desarrollado en Python Flask y desplegado en AWS.

## Características

- **Publicación Multi-Plataforma**: Soporte para Instagram, TikTok, X (Twitter) y Facebook
- **Arquitectura Modular**: Diseño escalable y mantenible con separación de responsabilidades
- **Gestión de Credenciales Segura**: No hay hard-coding de credenciales, uso de variables de entorno
- **Validación Robusta**: Validación de formatos, tamaños y duraciones según cada plataforma
- **Manejo de Errores Centralizado**: Sistema de mensajes estructurado y logging completo
- **Dockerización Completa**: Listo para despliegue en contenedores
- **Monitoreo y Salud**: Health checks y monitoreo automático
- **Base de Datos Relacional**: Integración con RDS MySQL para tracking de publicaciones

## Requisitos Previos

### Infraestructura AWS
- **EC2**: Instancia para el servicio (t3.medium recomendado)
- **RDS**: Base de datos MySQL 8.0+
- **S3**: Bucket para almacenamiento de videos
- **IAM**: Roles y políticas adecuadas

### Credenciales de Redes Sociales
- **Instagram**: Business Account ID + Access Token
- **TikTok**: Client Key, Client Secret, Access Token
- **X (Twitter)**: API Key, API Secret, Access Token, Access Token Secret
- **Facebook**: Page ID + Access Token

## Instalación y Configuración

### 1. Clonar y Configurar

```bash
# Clonar el repositorio
git clone https://github.com/christianfreire15/Socialman-App.git
cd root_proyect

# Copiar archivo de configuración
cp .env.example .env

# Editar variables de entorno
nano .env
```

### 2. Configurar Variables de Entorno

```bash
# Configuración AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name

# Base de Datos
RDS_HOST=your-rds-endpoint
RDS_DATABASE=socialman_db
RDS_USERNAME=your_username
RDS_PASSWORD=your_password

# Credenciales de Redes Sociales
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id
TIKTOK_CLIENT_KEY=your_key
# ... más credenciales
```

### 3. Configurar Base de Datos

```bash
# Conectar a RDS y ejecutar schema
mysql -h your-rds-endpoint -u username -p < database_schema.sql
```

### 4. Desplegar en EC2

```bash
# Hacer ejecutable el script de despliegue
chmod +x deploy-to-ec2.sh

# Ejecutar despliegue automático
./deploy-to-ec2.sh
```

## Despliegue con Docker

### Desarrollo Local
```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Producción
```bash
# Construir imagen optimizada
docker build -t socialman/video-publishing-service:latest .

# Ejecutar con configuración de producción
docker run -d \
  --name socialman-video-publisher \
  -p 5001:5001 \
  --env-file .env \
  socialman/video-publishing-service:latest
```

## API Endpoints

### 1. Health Check
```http
GET /health
```
**Respuesta:**
```json
{
  "success": true,
  "message": "Video Publishing Service is running successfully",
  "service": "SocialMan Video Publishing Service",
  "version": "1.0.0",
  "timestamp": "2025-08-14T10:30:00Z"
}
```

### 2. Publicar Video
```http
POST /publish
Content-Type: application/json

{
  "video_id": 123,
  "platforms": ["instagram", "tiktok", "x", "facebook"]
}
```

**Respuesta Exitosa:**
```json
{
  "success": true,
  "message": "Video published successfully to selected platforms",
  "data": {
    "video_id": 123,
    "successful_publications": [
      {
        "platform": "instagram",
        "status": "success",
        "publication_id": "ABC123",
        "url": "https://www.instagram.com/p/ABC123/"
      }
    ],
    "failed_publications": [],
    "total_platforms": 4,
    "successful_count": 4,
    "failed_count": 0
  },
  "timestamp": "2025-08-14T10:30:00Z"
}
```

### 3. Obtener Plataformas Disponibles
```http
GET /platforms
```

### 4. Estado de Publicación
```http
GET /status/{video_id}
```
## Configuración por Plataforma

### Instagram
- **Formato**: MP4, MOV
- **Tamaño máximo**: 100MB
- **Duración máxima**: 60 segundos
- **Caption**: Hasta 2,200 caracteres

### TikTok
- **Formato**: MP4, MOV, AVI
- **Tamaño máximo**: 128MB
- **Duración máxima**: 180 segundos
- **Caption**: Hasta 150 caracteres

### X (Twitter)
- **Formato**: MP4, MOV
- **Tamaño máximo**: 512MB
- **Duración máxima**: 140 segundos
- **Text**: Hasta 280 caracteres

### Facebook
- **Formato**: MP4, MOV, AVI
- **Tamaño máximo**: 1024MB
- **Duración máxima**: 240 segundos
- **Description**: Hasta 63,206 caracteres

## Seguridad

### Variables de Entorno
- Todas las credenciales se manejan via variables de entorno
- No hay hard-coding de claves en el código
- Archivo `.env` excluido del control de versiones

### Validaciones
- Validación de formatos de archivo por plataforma
- Límites de tamaño y duración aplicados
- Sanitización de inputs de usuario

### Red
- HTTPS obligatorio en producción
- Proxy reverso con Nginx
- Rate limiting implementado

## Monitoreo y Logs

### Health Checks
```bash
# Verificar estado del servicio
curl http://localhost:5001/health

# Verificar con Docker
docker exec socialman-video-publisher curl http://localhost:5001/health
```

### Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Logs específicos del servicio
docker logs socialman-video-publisher

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Métricas de Base de Datos
```sql
-- Ver estadísticas de publicación por plataforma
SELECT * FROM platform_statistics;

-- Resumen de publicaciones por video
SELECT * FROM publication_summary WHERE video_id = 123;
```

## Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a RDS
```bash
# Verificar conectividad
telnet your-rds-endpoint 3306

# Verificar credenciales
mysql -h your-rds-endpoint -u username -p
```

#### 2. Error de Credenciales de Redes Sociales
```bash
# Verificar variables de entorno
docker exec socialman-video-publisher env | grep INSTAGRAM
```

#### 3. Error de S3
```bash
# Verificar permisos IAM
aws s3 ls s3://your-bucket-name

# Verificar configuración AWS
aws configure list
```

#### 4. Servicio No Responde
```bash
# Reiniciar servicio
docker-compose restart

# Verificar recursos del sistema
docker stats socialman-video-publisher
```

### Logs de Debugging
```bash
# Habilitar modo debug
echo "DEBUG=true" >> .env
docker-compose restart

# Ver logs detallados
docker-compose logs -f video-publishing-service
```

## Actualización y Mantenimiento

### Actualizar Servicio
```bash
# Actualizar código
git pull origin main

# Reconstruir contenedor
docker-compose down
docker-compose up --build -d
```

### Backup de Base de Datos
```bash
# Crear backup
mysqldump -h your-rds-endpoint -u username -p socialman_db > backup.sql

# Restaurar backup
mysql -h your-rds-endpoint -u username -p socialman_db < backup.sql
```

### Limpieza de Sistema
```bash
# Limpiar imágenes Docker no utilizadas
docker image prune -f

# Limpiar logs antiguos
sudo find /var/log -name "*.log" -mtime +30 -delete
```

## Soporte

### Información de Contacto
- **Servicio**: SocialMan Video Publishing Service
- **Versión**: 1.0.0
- **Desarrollador**: SocialMan Development Team

## Licencia

Este proyecto está desarrollado para el curso de Programación en la Nube - Ingeniería de Software.

---

**Nota**: Este servicio forma parte del proyecto SocialMan App y debe ser usado en conjunto con el servicio principal de lectura y escritura de datos.
