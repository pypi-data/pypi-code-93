import unittest
import asyncio

from hannah.http.session import HTTPSession
from hannah.models import SwaggerService


class SwaggerServiceTestCase(unittest.TestCase):

    name: str = 'petstore'
    url: str = 'https://petstore.swagger.io'

    @classmethod
    def setUpClass(cls) -> None:
        cls.session = HTTPSession(cls.name, cls.url)
        cls.service = SwaggerService.from_url(cls.name, cls.url, cls.session, swagger_path='/v2/swagger.json')

    def test_swagger_service(self):
        print(asyncio.run(self.service.findPetsByStatus()))


if __name__ == '__main__':
    unittest.main()
