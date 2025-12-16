FROM python:3.13-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput --clear

# Exponer puerto
EXPOSE 8000

# Ejecutar migraciones e iniciar gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn nuestroproyecto.wsgi:application --bind 0.0.0.0:8000 --workers 3"]