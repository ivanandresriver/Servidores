from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Practica, Tour, Reserva
from .forms import LoginForm, RegistroForm, EditarUsuarioForm, TourForm
from django.db.models import Q # Import Q for complex queries
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

# --- Authentication Views ---
# Estas vistas manejan el registro, inicio y cierre de sesión de los usuarios.

def forgot_password_view(request):
    """
    Vista para manejar la recuperación de contraseña.
    1. Muestra un formulario para ingresar usuario o correo.
    2. Busca al usuario en la base de datos.
    3. Simula el envío de un correo (imprimiendo en consola) con un enlace de reset.
    """
    if request.method == "POST":
        identifier = request.POST.get('identifier')
        try:
            # Find user
            user = Practica.objects.get(Q(username=identifier) | Q(email=identifier))
            
            # Create a simple "token" (In production, use proper token generators)
            # For this simple project, we will just direct them to the reset page with their ID
            # WARNING: This isn't secure for production but fits the current scope "custom system"
            reset_url = request.build_absolute_uri(reverse('reset_password', args=[user.id]))
            
            # Send Email (to Console for now)
            message = f"Hola {user.username},\n\nPara restablecer tu contraseña, haz clic aquí:\n{reset_url}\n\nSi no fuiste tú, ignora este mensaje."
            send_mail(
                'Restablecer Contraseña - Travel Web',
                message,
                'noreply@travelweb.com',
                [user.email if user.email else 'unknown@example.com'],
                fail_silently=False,
            )
            
            messages.success(request, f'Se envió un enlace de recuperación a la consola (simulación de correo).')
            return redirect('login')
            
        except Practica.DoesNotExist:
            messages.error(request, 'No encontramos un usuario con ese correo o nombre.')
            
    return render(request, "password_reset_request.html")

def reset_password_view(request, user_id):
    """
    Vista para establecer una nueva contraseña.
    Se accede a través del enlace generado en 'forgot_password_view'.
    Recibe el ID del usuario para saber a quién cambiarle la clave.
    """
    try:
        user = Practica.objects.get(id=user_id)
    except Practica.DoesNotExist:
        return redirect('login')

    if request.method == "POST":
        p1 = request.POST.get('new_password')
        p2 = request.POST.get('confirm_password')
        
        if p1 == p2:
            user.password = p1 # Note: Should hash in production
            user.save()
            messages.success(request, 'Contraseña actualizada correctamente. Inicia sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')
            
    return render(request, "password_reset_confirm.html")

def home_view(request):
    """
    Vista principal para usuarios normales (NO administradores).
    Verifica que el usuario esté logueado (sesión activa) antes de mostrar la página.
    Muestra la página principal con tours organizados por categoría.
    """
    if 'user_id' not in request.session: 
        return redirect('login')
    
    # Obtener tours por categoría
    tours_lugares = Tour.objects.filter(categoria='lugar')
    tours_ciudades = Tour.objects.filter(categoria='ciudad')
    nombre_usuario = request.session.get('username')
    
    contexto = {
        'tours_lugares': tours_lugares,
        'tours_ciudades': tours_ciudades,
        'nombre_usuario': nombre_usuario
    }
    
    return render(request, "pagina_principal.html", contexto)

def login_view(request):
    """
    Vista de inicio de sesión general.
    - Procesa el formulario de login.
    - Verifica credenciales (usuario/email y contraseña).
    - Crea la sesión del usuario si los datos son correctos.
    - Redirige al Dashboard si es admin, o al Home si es usuario normal.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_input = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                # Check for either username OR email
                usuario = Practica.objects.get(Q(username=username_input) | Q(email=username_input))
                
                if usuario.password == password:
                    request.session['user_id'] = usuario.id
                    request.session['username'] = usuario.username
                    
                    if usuario.is_admin:
                        messages.success(request, f'Bienvenido Admin {usuario.username}!')
                        return redirect('dashboard')
                    else:
                        messages.success(request, f'Bienvenido {usuario.username}!')
                        return redirect('home')
                        
                else:
                    form.add_error('password', 'Contraseña incorrecta')
            except Practica.DoesNotExist:
                form.add_error('username', 'Usuario o Email no encontrado')
            except Practica.MultipleObjectsReturned:
                # Fallback if both email and username match identical string (unlikely but possible)
                form.add_error('username', 'Error: Multiples usuarios encontrados')
                
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

def login_admin_view(request):
    """Vista exclusiva para administradores"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_input = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                # Check for either username OR email
                usuario = Practica.objects.get(Q(username=username_input) | Q(email=username_input))
                
                if usuario.password == password:
                    if usuario.is_admin:
                        request.session['user_id'] = usuario.id
                        request.session['username'] = usuario.username
                        messages.success(request, f'Bienvenido al Panel, {usuario.username}')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Acceso Denegado: Esta cuenta no es de administrador.')
                else:
                    form.add_error('password', 'Contraseña incorrecta')
            except Practica.DoesNotExist:
                form.add_error('username', 'Usuario o Email no encontrado')
    else:
        form = LoginForm()
    return render(request, "login_admin.html", {'form': form})

def logout_view(request):
    """
    Cierra la sesión del usuario actual.
    Elimina todos los datos de la sesión (flush) y redirige al login.
    """
    username = request.session.get('username', 'Usuario')
    request.session.flush()
    messages.success(request, f'{username}, has cerrado sesión correctamente')
    return redirect("login")

def formulario(request): # Register View
    """
    Vista de Registro de nuevos usuarios.
    - Validar datos del formulario (RegistroForm).
    - Guardar el nuevo usuario en la base de datos.
    - Encriptar/Asignar contraseña y URL de imagen.
    """
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.password = form.cleaned_data['password1']
            
            # Form automatically handles username, email, nombre, apellido via Meta.fields
            # Just handling custom manual saves if needed, or let form.save() do it.
            # However, we are getting commit=False to hash password.
            
            imagen_url = form.cleaned_data.get('imagen_url')
            if imagen_url:
                usuario.imagen_url = imagen_url
            usuario.save()
            messages.success(request, 'Usuario registrado exitosamente. ¡Inicia sesión!')
            return redirect("login")
    else:
        form = RegistroForm()
    return render(request, "Registro.html", {'form': form})

# --- Dashboard & Tour Views ---

def dashboard(request):
    """
    Panel de Control Principal (Dashboard) - Solo para Administradores.
    - Verifica que el usuario esté logueado y sea admin.
    - Obtiene estadísticas y listas (Toures, Personas recientes) para mostrar.
    - Búsqueda de tours por nombre.
    """
    if 'user_id' not in request.session:
         return redirect('login')
    
    # Security: Ensure only admins can access dashboard
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        if not user.is_admin:
            return redirect('home') # Redirect non-admins to home
    except Practica.DoesNotExist:
         return redirect('login')

    # Get search query from GET parameters
    search_query = request.GET.get('buscar', '')
    
    # Filter tours by name if search query exists
    if search_query:
        tours = Tour.objects.filter(nombre__icontains=search_query)
    else:
        tours = Tour.objects.all()
    
    personas = Practica.objects.all().order_by('-id')[:5] # Last 5 users
    username = request.session.get('username')
    
    context = {
        'tours': tours,
        'personas': personas,
        'username': username,
        'search_query': search_query,  # Pass search query to template
    }
    return render(request, "dashboard.html", context)

def crear_tour(request):
    """
    Vista para crear un nuevo Tour.
    - Solo accesible para admins.
    - Usa 'TourForm' para facilitar la creación y validación.
    - Maneja la subida de archivos (imágenes).
    """
    if 'user_id' not in request.session: return redirect('login')
    
    # Secure: Only Admin
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        if not user.is_admin: return redirect('tours') # or home
    except Practica.DoesNotExist: return redirect('login')

    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tours') # Redirect to tours list instead of dashboard for better UX? Or keep dashboard. User said "users no crud", admins do.
            # Let's redirect to dashboard if admin, but tours is fine too. Let's keep dashboard as it was behavior.
            # Actually, let's redirect to 'tours' since we are editing tours there mostly now? 
            # ORIGINAL behavior was redirect('dashboard'). I will keep it but maybe 'tours' is better if we just came from there.
            return redirect('dashboard')
    else:
        form = TourForm()
    return render(request, "tour_form.html", {'form': form, 'title': 'Crear Tour'})

def editar_tour(request, pk):
    if 'user_id' not in request.session: return redirect('login')
    
    # Secure: Only Admin
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        if not user.is_admin: return redirect('tours')
    except Practica.DoesNotExist: return redirect('login')

    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            return redirect('tours') # Redirect to tours list is usually better context
    else:
        form = TourForm(instance=tour)
    return render(request, "tour_form.html", {'form': form, 'title': 'Editar Tour'})

def eliminar_tour(request, pk):
    if 'user_id' not in request.session: return redirect('login')
    
    # Secure: Only Admin
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        if not user.is_admin: return redirect('tours')
    except Practica.DoesNotExist: return redirect('login')

    tour = get_object_or_404(Tour, pk=pk)
    tour.delete()
    return redirect('tours')

# --- User Management Views (Legacy/Admin) ---

def user_register(request):
    """
    Vista de gestión de usuarios (Admin).
    - Lista todos los usuarios registrados
    - Permite eliminar usuarios
    - Incluye funcionalidad de búsqueda por username, email o nombre
    """
    if 'user_id' not in request.session: return redirect("login")
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            usuario = Practica.objects.get(id=user_id)
            usuario.delete()
            messages.success(request, f'Usuario eliminado')
        except Practica.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
        return redirect("user_register")
    
    # Obtener término de búsqueda
    query = request.GET.get('q', '').strip()
    
    # Filtrar usuarios si hay búsqueda
    if query:
        usuarios = Practica.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(nombre__icontains=query)
        ).order_by('username')
    else:
        usuarios = Practica.objects.all().order_by('username')
    
    usuario_actual_id = request.session.get('user_id')
    return render(request, "UserRegister.html", {
        'usuarios': usuarios,
        'usuario_actual_id': usuario_actual_id,
        'total_usuarios': usuarios.count(),
        'query': query
    })

def editar_usuario(request, user_id):
    if 'user_id' not in request.session: return redirect("login")
    try: usuario = Practica.objects.get(id=user_id)
    except Practica.DoesNotExist: return redirect("user_register")

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            u = form.save(commit=False)
            if form.cleaned_data.get('password1'): u.password = form.cleaned_data['password1']
            if form.cleaned_data.get('imagen_url'): u.imagen_url = form.cleaned_data.get('imagen_url')
            u.save()
            return redirect("user_register")
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, "editar_usuario.html", {'form': form, 'usuario': usuario, 'es_edicion': True})

# --- Simple Views (Legacy) ---
def saludo(request): return HttpResponse("Hola mundo")
def despedida(request): return HttpResponse("Hasta luego")
def anime(request): return render(request, "./anime.html")
def mundo(request): return render(request, "./plantilla.html")

def tours_view(request):
    """
    Vista pública/mixta para ver el listado de Tours.
    - Separa los tours en categorías (Ciudad, Lugar) para mostrarlos organizados.
    - Pasa la variable 'is_admin' para mostrar botones de edición solo a admins.
    - Incluye funcionalidad de búsqueda por nombre o descripción
    """
    if 'user_id' not in request.session:
         return redirect('login')
    
    # Determine if Admin
    is_admin = False
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        is_admin = user.is_admin
    except Practica.DoesNotExist:
        pass

    # Obtener término de búsqueda
    query = request.GET.get('q', '').strip()
    
    # Filtrar tours si hay búsqueda
    if query:
        tours_ciudades = Tour.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query),
            categoria='ciudad'
        )
        tours_lugares = Tour.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query),
            categoria='lugar'
        )
    else:
        tours_ciudades = Tour.objects.filter(categoria='ciudad')
        tours_lugares = Tour.objects.filter(categoria='lugar')
    
    username = request.session.get('username')
    
    context = {
        'tours_ciudades': tours_ciudades,
        'tours_lugares': tours_lugares,
        'username': username,
        'is_admin': is_admin,
        'query': query
    }
    return render(request, "tours.html", context)

def perfil_view(request):
    """
    Vista de 'Mi Perfil'.
    - Permite al usuario logueado editar sus propios datos.
    - Maneja cambios de contraseña, imagen y datos personales.
    - Actualiza la sesión si cambia el nombre de usuario.
    """
    if 'user_id' not in request.session: return redirect('login')
    
    try:
        usuario = Practica.objects.get(id=request.session['user_id'])
    except Practica.DoesNotExist:
        return redirect('login')

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            u = form.save(commit=False)
            if form.cleaned_data.get('password1'): u.password = form.cleaned_data['password1']
            if form.cleaned_data.get('imagen_url'): u.imagen_url = form.cleaned_data.get('imagen_url')
            u.save()
            messages.success(request, 'Perfil actualizado correctamente')
            request.session['username'] = u.username 
            return redirect("perfil")
    else:
        form = EditarUsuarioForm(instance=usuario)
    
    return render(request, "perfil.html", {'form': form, 'username': usuario.username, 'usuario': usuario})

def configuracion_view(request):
    """
    Vista de Configuración del Sistema.
    - Muestra opciones globales como Idioma y Notificaciones.
    - Por ahora es visual, la lógica se maneja en el frontend o se guardará en futuras versiones.
    """
    if 'user_id' not in request.session: return redirect('login')
    
    # Just render the template, settings will be handled via JS/LocalStorage for now or simple form if backend needed
    try:
        usuario = Practica.objects.get(id=request.session['user_id'])
    except Practica.DoesNotExist:
        return redirect('login')
        
    return render(request, "configuracion.html", {'username': usuario.username, 'usuario': usuario})

def explorar_toures_view(request):
    """
    Vista de exploración de tours para usuarios.
    Muestra todos los tours disponibles con detalles de reserva.
    Accesible para usuarios logueados (admin y usuarios normales).
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Obtener todos los tours disponibles
    tours = Tour.objects.all()
    nombre_usuario = request.session.get('username')
    
    contexto = {
        'tours': tours,
        'nombre_usuario': nombre_usuario
    }
    
    return render(request, "explorar_toures.html", contexto)

def sobre_nosotros_view(request):
    """
    Vista de 'Sobre Nosotros'.
    Muestra información de la empresa, logros, testimonios y ventajas.
    Accesible para todos los usuarios (con o sin login para facilitar acceso público).
    """
    nombre_usuario = request.session.get('username', None)
    
    contexto = {
        'nombre_usuario': nombre_usuario
    }
    
    return render(request, "sobre_nosotros.html", contexto)

def reservas_view(request):
    """
    Vista de Reservas.
    Permite a los usuarios hacer reservas de tours.
    Muestra un formulario simple con selección de tour y datos básicos.
    Guarda la reserva en la base de datos.
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Obtener todos los tours disponibles para el selector
    tours = Tour.objects.all()
    nombre_usuario = request.session.get('username')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            tour_id = request.POST.get('tour')
            nombre_cliente = request.POST.get('nombre')
            email_cliente = request.POST.get('email')
            telefono_cliente = request.POST.get('telefono')
            fecha_inicio = request.POST.get('fecha')
            numero_personas = request.POST.get('personas')
            observaciones = request.POST.get('observaciones', '')
            
            # Obtener tour y usuario
            tour = Tour.objects.get(id=tour_id)
            usuario = Practica.objects.get(id=request.session['user_id'])
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                tour=tour,
                usuario=usuario,
                nombre_cliente=nombre_cliente,
                email_cliente=email_cliente,
                telefono_cliente=telefono_cliente,
                fecha_inicio=fecha_inicio,
                numero_personas=numero_personas,
                observaciones=observaciones
            )
            
            messages.success(request, f'¡Reserva creada exitosamente para {nombre_cliente}! Tu reserva está pendiente de confirmación.')
            return redirect('reservas')
            
        except Tour.DoesNotExist:
            messages.error(request, 'El tour seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
    
    contexto = {
        'tours': tours,
        'nombre_usuario': nombre_usuario
    }
    
    return render(request, "reservas.html", contexto)

def reservas_admin_view(request):
    """
    Vista de Gestión de Reservas para Administradores.
    Muestra todas las reservas realizadas por los usuarios.
    Solo accesible para administradores.
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Verificar que sea administrador
    try:
        user = Practica.objects.get(id=request.session['user_id'])
        if not user.is_admin:
            return redirect('home')
    except Practica.DoesNotExist:
        return redirect('login')
    
    # Obtener todas las reservas ordenadas por fecha de creación
    reservas = Reserva.objects.all().select_related('tour', 'usuario')
    
    contexto = {
        'reservas': reservas,
        'username': request.session.get('username')
    }
    
    return render(request, "reservas_admin.html", contexto)

