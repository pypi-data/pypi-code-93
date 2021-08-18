import requests, json, logging

class UnileverController:

    @classmethod
    def authenticate(self, url, auth):
        headers = dict()
        headers['Content-Type'] = 'application/json'

        r = requests.post(f'{url}/auth',
            headers=headers,
            data=json.dumps(auth)
        )

        if r.status_code == 200:
            logging.info(f'Login to unilever... [{r.status_code}]')
        else:
            logging.error(f'Failed to login unilever [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def upload_product(self, url, token, product):
        headers = dict()
        headers['Authorization'] = f'Basic {token}'
        headers['Content-Type'] = 'application/json'
        
        r = requests.post(f'{url}/products',
            headers=headers,
            data=json.dumps(product)
        )

        if r.status_code == 200:
            logging.info(f'Product sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to send Product [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def upload_product_stock(self, url, token, product_stock):
        headers = dict()
        headers['Authorization'] = f'Basic {token}'
        headers['Content-Type'] = 'application/json'
        
        r = requests.post(f'{url}/productstock',
            headers=headers,
            data=json.dumps(product_stock)
        )

        if r.status_code == 200:
            logging.info(f'Product stock sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to sent product stock [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def upload_product_price(self, url, token, product_price):
        headers = dict()
        headers['Authorization'] = f'Basic {token}'
        headers['Content-Type'] = 'application/json'

        r = requests.post(f'{url}/productprice',
            headers=headers,
            data=json.dumps(product_price)
        )

        if r.status_code == 200:
            logging.info(f'Product price sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to sent product price [{r.status_code}] - {r.content.decode("utf-8")}')

        return r
