"""
Script para poblar la base de datos con tours de ejemplo
Ejecutar con: python poblar_tours.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuestroproyecto.settings')
django.setup()

from vistas.models import Tour

def crear_tours_ejemplo():
    """Crea tours de ejemplo para mostrar en la página principal"""
    
    # Limpiar tours existentes (opcional, comentar si deseas mantener los existentes)
    # Tour.objects.all().delete()
    
    # Tours de Lugares
    tours_lugares = [
        {
            'nombre': 'Cartagena',
            'descripcion': 'Hermosa ciudad costera con playas paradisíacas',
            'imagen_url': 'https://images.unsplash.com/photo-1568632234157-ce7aecd03d0d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '7.5M',
            'categoria': 'lugar'
        },
        {
            'nombre': 'Santa Marta',
            'descripcion': 'Ciudad histórica con playas hermosas y montañas',
            'imagen_url': 'https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '6 días de viaje',
            'precio': '10.5M',
            'categoria': 'lugar'
        },
        {
            'nombre': 'Guajira',
            'descripcion': 'Desierto, playas y cultura Wayuu',
            'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '5 días de viaje',
            'precio': '20.5M',
            'categoria': 'lugar'
        },
        {
            'nombre': 'Acuario',
            'descripcion': 'Espectacular acuario submarino con vida marina',
            'imagen_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '12 días de viaje',
            'precio': '4.5M',
            'categoria': 'lugar'
        },
        {
            'nombre': 'Sierra Nevada',
            'descripcion': 'Montañas nevadas y paisajes impresionantes',
            'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '6.9M',
            'categoria': 'lugar'
        },
        {
            'nombre': 'Ciudad Perdida',
            'descripcion': 'Antigua ciudad de la cultura Tayrona',
            'imagen_url': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '6.9M',
            'categoria': 'lugar'
        },
    ]
    
    # Tours de Ciudades
    tours_ciudades = [
        {
            'nombre': 'Cartagena',
            'descripcion': 'Ciudad amurallada con arquitectura colonial',
            'imagen_url': 'https://images.unsplash.com/photo-1568632234157-ce7aecd03d0d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '7.5M',
            'categoria': 'ciudad'
        },
        {
            'nombre': 'Santa Marta',
            'descripcion': 'La ciudad más antigua de Colombia',
            'imagen_url': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '6 días de viaje',
            'precio': '10.5M',
            'categoria': 'ciudad'
        },
        {
            'nombre': 'Guajira',
            'descripcion': 'Territorio indígena con paisajes únicos',
            'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '6 días de viaje',
            'precio': '30.5M',
            'categoria': 'ciudad'
        },
        {
            'nombre': 'Acuario',
            'descripcion': 'Parque temático marino en la costa',
            'imagen_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '4 días de viaje',
            'precio': '4.5M',
            'categoria': 'ciudad'
        },
        {
            'nombre': 'Sierra Nevada',
            'descripcion': 'Región montañosa con pueblos indígenas',
            'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '6.9M',
            'categoria': 'ciudad'
        },
        {
            'nombre': 'Ciudad Perdida',
            'descripcion': 'Sitio arqueológico milenario',
            'imagen_url': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            'duracion': '7 días de viaje',
            'precio': '6.9M',
            'categoria': 'ciudad'
        },
    ]
    
    # Crear tours de lugares
    print("Creando tours de lugares...")
    for datos_tour in tours_lugares:
        tour, creado = Tour.objects.get_or_create(
            nombre=datos_tour['nombre'],
            categoria='lugar',
            defaults=datos_tour
        )
        if creado:
            print(f"[OK] Creado: {tour.nombre} (Lugar)")
        else:
            print(f"[-] Ya existe: {tour.nombre} (Lugar)")
    
    # Crear tours de ciudades
    print("\nCreando tours de ciudades...")
    for datos_tour in tours_ciudades:
        tour, creado = Tour.objects.get_or_create(
            nombre=datos_tour['nombre'],
            categoria='ciudad',
            defaults=datos_tour
        )
        if creado:
            print(f"[OK] Creado: {tour.nombre} (Ciudad)")
        else:
            print(f"[-] Ya existe: {tour.nombre} (Ciudad)")
    
    print(f"\n¡Listo! Total de tours en la base de datos: {Tour.objects.count()}")

if __name__ == '__main__':
    crear_tours_ejemplo()
