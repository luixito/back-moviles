from datetime import datetime, timedelta
from functools import wraps
import jwt
import firebase_admin
from firebase_admin import credentials, firestore, storage
from flask import request, jsonify
from model import Mascota, Usuario
from flask import Flask, request, jsonify

clave = "IxAH7SjefD_IfpquIJP2a3ukYMs0E0s4MU-44jAgxSI"

app = Flask(__name__)

# Ruta al archivo de configuración de Firebase descargado
cred = credentials.Certificate("imagensCout.json")

# Inicializar la aplicación de Firebase con el nombre del bucket
firebase_admin.initialize_app(cred, options={
    'storageBucket': 'back-flutter-a83ed.appspot.com'
})
# Obtén una referencia a la colección en Firestore
db_firestore = firestore.client()

# Clave secreta para firmar y verificar tokens JWT
app.config['SECRET_KEY'] = clave

#Genera un token
def generar_token(datos, tiempo_expiracion_minutos):
    expiracion = datetime.utcnow() + timedelta(minutes=tiempo_expiracion_minutos)
    datos['exp'] = expiracion.timestamp() # Agregar fecha de expiración al payload
    token = jwt.encode(datos, app.config['SECRET_KEY'], algorithm='HS256')
    return token

#Verifica el token
def verificar_token(token):
    try:
        datos = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        expiracion_timestamp = datos.get('exp')

        if expiracion_timestamp:
            expiracion = datetime.fromtimestamp(expiracion_timestamp)

            if datetime.utcnow() < expiracion:
                # El token es válido y no ha expirado
                return datos

        # El token ha expirado o la comparación de fechas ha fallado
        return None
    except jwt.ExpiredSignatureError:
        # El token ha expirado
        return None
    except jwt.InvalidTokenError:
        # El token es inválido
        return None

#Si tiene permiso o no para acceder a la ruta       
def requerir_token(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')

        if token:
            # Verificar el token JWT
            datos = verificar_token(token)

            if datos:
                # El token es válido y no ha expirado, se permite el acceso a la ruta protegida
                return f(*args, **kwargs)

        # El token es inválido o no se proporcionó
        return jsonify({'message': 'Acceso no autorizado'}), 401

    return decorador

def registrar_mascota():
    nombre = request.form['nombre']
    raza = request.form['raza']
    image = request.files['image']
    horario = request.form['horario']
    ubicacion = request.form['ubicacion']

    mascota = Mascota(nombre, raza, image, horario, ubicacion)
    mascota.guardar_en_firestore()

    return 'Registro de la mascota exitoso'

def registrar_usuario():
    nombre = request.form['nombre']
    email = request.form['email']
    ciudadEstado = request.form['ciuadadEstado']
    contrasena = request.form['contrasena']

    usuario = Usuario(nombre, email, ciudadEstado, contrasena)
    usuario.guardar_en_firestore()

    return 'Registro de usuario exitoso'

def iniciar_sesion():
    email = request.args.get('email')
    contrasena = request.args.get('contrasena')

    # Verificar las credenciales en Firestore
    users_ref = db_firestore.collection('register')
    query = users_ref.where('email', '==', email).where('contrasena', '==', contrasena).limit(1)
    results = query.get()

    if len(results) > 0:
        # Las credenciales son válidas
        user_data = results[0].to_dict()
        # Generar token JWT con los datos del usuario (válido por 30 minutos)
        token = generar_token(user_data, tiempo_expiracion_minutos=10)
        return jsonify({'message': 'Inicio de sesión exitoso', 'user': user_data, 'token': token})
    else:
        # Las credenciales son inválidas
        return jsonify({'message': 'Credenciales inválidas'})

def obtener_mascotas_adoptadas():
    # Obtener una referencia a la colección "FormAdopted"
    db_firestore = firestore.client()
    form_adopted_ref = db_firestore.collection('FormAdopted')

    # Obtener todos los documentos de la colección
    documents = form_adopted_ref.get()

    # Crear una lista para almacenar los datos
    data = []

    # Recorrer los documentos y agregar sus datos a la lista
    for doc in documents:
        data.append(doc.to_dict())

    # Devolver los datos en formato JSON
    return jsonify(data)
