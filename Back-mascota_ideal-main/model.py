from firebase_admin import credentials, firestore, storage
import uuid

class Mascota:
    def __init__(self, nombre, raza, image, horario, ubicacion):
        self.nombre = nombre
        self.raza = raza
        self.image = image
        self.horario = horario
        self.ubicacion = ubicacion

    def guardar_en_firestore(self):
        # Obtén una referencia a la colección en Firestore
        db_firestore = firestore.client()

        # Generar un ID único para el registro
        document_id = str(uuid.uuid4())

        # Guardar la imagen en Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(f'formAdopted/{self.image.filename}')

        # Agregar el encabezado "Content-Type"
        blob.content_type = 'image/jpeg'

        blob.upload_from_file(self.image)

        # Almacenar los datos en Firestore
        data_firestore = {
            'nombre': self.nombre,
            'raza': self.raza,
            'image': self.image.filename,
            'horario': self.horario,
            'ubicacion': self.ubicacion,
        }
        db_firestore.collection('FormAdopted').document(document_id).set(data_firestore)

class Usuario:
    def __init__(self, nombre, email, ciudad_estado, contrasena):
        self.nombre = nombre
        self.email = email
        self.ciudad_estado = ciudad_estado
        self.contrasena = contrasena

    def guardar_en_firestore(self):
        # Obtén una referencia a la colección en Firestore
        db_firestore = firestore.client()

        # Generar un ID único para el registro
        document_id = str(uuid.uuid4())

        # Almacenar los datos en Firestore
        data_firestore = {
            'nombre': self.nombre,
            'email': self.email,
            'ciudadEstado': self.ciudad_estado,
            'contrasena': self.contrasena,
        }
        db_firestore.collection('register').document(document_id).set(data_firestore)

