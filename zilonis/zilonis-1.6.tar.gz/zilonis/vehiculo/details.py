import requests, json
from zilonis.constantes import constantes

def getMarcas(token):
    url = constantes.API+'/api/v1/cotizacion/marcas'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json


def getSubMarcas(token, idmarca):
    url = constantes.API+'/api/v1/cotizacion/marca/'+str(idmarca)+'/submarcas'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json

def getModelos(token, idsubmarca):
    url = constantes.API+'/api/v1/cotizacion/submarca/'+str(idsubmarca)+'/modelos'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json


def getDescripcion(token, idsubmarca, idmodelo):
    url = constantes.API+'/api/v1/cotizacion/submarca/'+str(idsubmarca)+'/modelo/'+str(idmodelo)+'/descripciones'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json