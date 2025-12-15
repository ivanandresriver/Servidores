# Usa una imagen base ligera de Python
FROM python:3.11-alpine

# Establece variables de entorno para que Python no escriba .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Instala dependencias del sistema operativo (si son necesarias para tu aplicación o dependencias)
# Ejemplo: si usas Pillow o PostgreSQL cliente:
# RUN apk add --no-cache gcc musl-dev postgresql-dev

# Copia el archivo de requerimientos e instala dependencias ANTES del código para aprovechar el cache de Docker
COPY requirements.txt /usr/src/app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo el código fuente del proyecto
COPY . /usr/src/app/

# Ejecuta comandos de Django (asegúrate de que Django ya esté configurado para base de datos)
RUN python manage.py collectstatic --no-input

# Exponer el puerto donde se ejecutará Gunicorn (el servidor de producción para Django)
EXPOSE 8000

# Comando para iniciar la aplicación (usa Gunicorn en producción)
# Reemplaza 'tu_proyecto.wsgi' con la ruta real a tu archivo WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tu_proyecto.wsgi:application"]