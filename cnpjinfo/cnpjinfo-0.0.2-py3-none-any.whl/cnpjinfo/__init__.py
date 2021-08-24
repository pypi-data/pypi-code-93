from requests import get

__version__ = '0.0.2'

def cnpjinfo(cnpj):
    """Get cnpj information via scraping from the cnpj.info website."""

    response = get('https://www.receitaws.com.br/v1/cnpj/' + cnpj)

    try:
        data = response.json()
    except:
        data = None
    
    return data


if __name__ == "__main__":
    ...