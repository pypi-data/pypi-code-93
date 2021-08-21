import requests, json
from zilonis.constantes import constantes

def getLogin(user, pase):
    url = constantes.API+'/api/v1/usuario/login'
    headers = {'Content-Type': 'application/json'}
    args = {'username':user,'password':pase}
    response = requests.post(url, json=args, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    elif response.status_code == 404:
        response_json = {'Error':'Usuario no encontrado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json

def regUsuario(**data):
    url = constantes.API+'/api/v1/usuario/crear'
    headers = headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=data, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    elif response.status_code == 400:
        response_json = {'Error':'Usuario ya existe'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json

def insertaClaves(token, **data):
    url = constantes.API+'/api/v1/usuario/save/claveagente'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.post(url, json=data, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json