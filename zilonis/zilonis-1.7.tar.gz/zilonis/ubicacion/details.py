import requests, json
from zilonis.constantes import constantes

def getEstados(token):
    url = constantes.API+'/api/v1/cotizacion/estados'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json


def getMunicipios(token, idestado):
    url = constantes.API+'/api/v1/cotizacion/estado/'+str(idestado)+'/municipios'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json


def getColonias(token, idmunicipio):
    url = constantes.API+'/api/v1/cotizacion/municipio/'+str(idmunicipio)+'/colonias'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json


def getCodigosPostales(token, idcodigo):
    url = constantes.API+'/api/v1/cotizacion/codigopostal/'+str(idcodigo)+'/codigospostales'
    headers = {'Accept':'application/json','Authorization':'Bearer '+token}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json = json.loads(response.text)
    elif response.status_code == 401:
        response_json = {'Error':'Acceso Denegado'}
    else:
        response_json = {'Error':'Servicio fuera linea'}

    return response_json