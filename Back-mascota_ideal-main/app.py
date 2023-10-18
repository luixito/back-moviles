from flask import Flask, request
import controller

app = Flask(__name__)

#Registro de mascotas
@app.route('/formAdopted', methods=['POST'])
@controller.requerir_token
def registrar_mascota():
    return controller.registrar_mascota()

#Registro del usuario
@app.route('/register', methods=['POST'])
def registrar_usuario():
    return controller.registrar_usuario()

#login
@app.route('/login', methods=['GET'])
def iniciar_sesion():
    return controller.iniciar_sesion()

#Obtener mascotas adoptadas
@app.route('/getAdopted', methods=['GET'])
@controller.requerir_token
def obtener_mascotas_adoptadas():
    return controller.obtener_mascotas_adoptadas()

if __name__ == '__main__':
    app.run()
