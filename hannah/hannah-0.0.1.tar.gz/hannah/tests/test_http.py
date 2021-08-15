import unittest
import asyncio

from hannah.http.session import HTTPSession, HTTPStatusError


class HTTPSessionTestCase(unittest.TestCase):

    name: str = 'Users'
    url: str = 'https://reqres.in'

    @classmethod
    def setUpClass(cls) -> None:
        cls.session = HTTPSession(cls.name, cls.url)

    def test_session_auth(self):
        auth = ('Bearer', '234234233252352523')
        self.session.set_auth(*auth)
        self.assertEqual(self.session.headers['Authorization'], '{} {}'.format(*auth))

    def test_200_ok(self):
        traffic = asyncio.run(self.session.request('GET', '/api/users'))
        self.assertEqual(traffic.response.status, 200)
        self.assertIsInstance(traffic.response.body, dict)
        self.assertEqual(traffic.response.body['page'], 1)

    def test_404_not_found(self):
        traffic = asyncio.run(self.session.request('GET', '/api/users/unknown'))
        self.assertEqual(traffic.response.status, 404)

    def test_404_not_found_with_raise_status_error(self):
        with self.assertRaises(HTTPStatusError):
            session = HTTPSession(self.name, self.url, raise_on_non_2xx_error=True)
            asyncio.run(session.request('GET', '/api/user/unknown'))


if __name__ == '__main__':
    unittest.main()
