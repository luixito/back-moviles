from fileinput import filename
from tkinter import Variable
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps

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

#Genera un tokens
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



#Registro de mascotas
@app.route('/formAdopted', methods=['POST'])
@requerir_token
def forms():
    # Obtener los datos enviados en la solicitud POST
    nombre = request.form['nombre']
    raza = request.form['raza']
    image = request.files['image']
    horario = request.form['horario']
    ubicacion = request.form['ubicacion']
    
    
    #se obtiene el nombre original de la imagen
    filename = image.filename
    # Generar un ID único para el registro
    document_id = str(uuid.uuid4())

    # Guardar la imagen en Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f'formAdopted/{filename}')
    
    # Agregar el encabezado "Content-Type"
    blob.content_type = 'image/jpeg'
    
    blob.upload_from_file(image)

    # Almacenar los datos en Firestore
    db_firestore = firestore.client()
    data_firestore = {
        'nombre': nombre,
        'raza': raza,
        'image': filename,
        'horario': horario,
        'ubicacion' : ubicacion,
    }
    db_firestore.collection('FormAdopted').document(document_id).set(data_firestore)

    return 'Registro de la mascota exitoso'

#Regirstro del usuario
@app.route('/register', methods = ['POST'])
def register ():
    nombre = request.form['nombre']
    email = request.form['email']
    ciudadEstado = request.form['ciuadadEstado']
    contrasena = request.form['contrasena']

    document_id = str(uuid.uuid4())

    # Almacenar los datos en Firestore
    db_firestore = firestore.client()
    data_firestore = {
        'nombre': nombre,
        'email': email,
        'ciudadEstado': ciudadEstado,
        'contrasena': contrasena,
    }
    db_firestore.collection('register').document(document_id).set(data_firestore)

    return 'Registro de la mascota exitoso'


#login
@app.route('/login', methods = ['GET'])
def login():
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


#=====================
@app.route('/getAdopted', methods=['GET'])
@requerir_token
def get_form_adopted():
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


if __name__ == '__main__':
    app.run()
