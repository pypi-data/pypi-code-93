import requests


class GamepayPyException(Exception):
    pass


class GamepayPy():

    def __init__(self, token):
        self.token = token

    # Создание ссылки для оплаты:
    def createOrder(self, unique_id, amount, shop_id, description):

        response = requests.post("https://gamepay.best/api/createOrder",
                                 data={"token": str(self.token),
                                       "unique": int(unique_id),
                                       "amount": int(amount),
                                       "shop_id": int(shop_id),
                                       "description": str(description)}).json()


        try:
            if response['data']['link']:
                return response['data']['link']

        except KeyError:
            raise GamepayPyException(f"Error: [{response['data']['error']}] {response['data']['mess']}")

    # Проверка статуса заказа:
    def checkStatus(self, order_id):

        response = requests.post("https://gamepay.best/api/checkStatus",
                                 data={"token": str(self.token),
                                       "order_id": int(order_id)}).json()

        try:
            if response['data']['status']:
                return response['data']['status']

        except KeyError:
            raise GamepayPyException(f"Error: [{response['data']['error']}] {response['data']['mess']}")

    # Получение баланса аккаунта:
    def checkBalance(self):

        response = requests.post("https://gamepay.best/api/checkBalance",
                                 data={"token": str(self.token)}).json()

        try:
            if response['data']['balance']:
                return float(response['data']['balance'])

        except KeyError:
            raise GamepayPyException(f"Error: [{response['data']['error']}] {response['data']['mess']}")
