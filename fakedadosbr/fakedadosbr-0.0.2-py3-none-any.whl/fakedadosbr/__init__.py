from random import randint, choice, random
from requests import post
from bs4 import BeautifulSoup


__version__ = '0.0.2'


def fake_cidadao(qtde=1):
    """ Gera dados de pessoa para desenvolvimento. """
    data = {'acao':'gerar_pessoa', 'txt_qtde':str(qtde)}
    response = post('https://www.4devs.com.br/ferramentas_online.php', data)
    try:
        data = response.json()
    except:
        data = None
    return data


def fake_empresa(qtde=1):
    """ Gera dados de empresa para desenvolvimento. """

    estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    idade = randint(1,30)

    data = {'acao':'gerar_empresa', 'estado':choice(estados), 'idade':str(idade)}
    response = post('https://www.4devs.com.br/ferramentas_online.php', data)
    try:
        data = {}
        html = BeautifulSoup(response.text, "html.parser")
        data["nome"] = html.find(id="nome").get('value')
        data["cnpj"] = html.find(id="cnpj").get('value')
        data["ie"] = html.find(id="ie").get('value')
        data["data_abertura"] = html.find(id="data_abertura").get('value')
        data["site"] = html.find(id="site").get('value')
        data["email"] = html.find(id="email").get('value')
        data["cep"] = html.find(id="cep").get('value')
        data["endereco"] = html.find(id="endereco").get('value')
        data["numero"] = html.find(id="numero").get('value')
        data["cidade"] = html.find(id="cidade").get('value')
        data["estado"] = html.find(id="estado").get('value')
        data["telefone_fixo"] = html.find(id="telefone_fixo").get('value')
        data["celular"] = html.find(id="celular").get('value')
    except:
        data = None
    return data


def fake_veiculo(qtde=1):
    """ Gera dados de veiculos para desenvolvimento. """

    estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

    data = {'acao':'gerar_veiculo', 'estado':choice(estados)}
    response = post('https://www.4devs.com.br/ferramentas_online.php', data)
    try:
        data = {}
        html = BeautifulSoup(response.text, "html.parser")
        data["marca"] = html.find(id="marca").get('value')
        data["modelo"] = html.find(id="modelo").get('value')
        data["ano"] = html.find(id="ano").get('value')
        data["renavam"] = html.find(id="renavam").get('value')
        data["placa_veiculo"] = html.find(id="placa_veiculo").get('value')
        data["cor"] = html.find(id="cor").get('value')
    except:
        data = None
    return data


if __name__ == "__main__":
    ...
