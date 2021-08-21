import requests
import unittest


@unittest.skip
class RequestTest(unittest.TestCase):
    def test_get_returns_200(self):
        r = requests.get("https://jsonplaceholder.typicode.com/todos/1")
        self.assertEqual(r.status_code, 200)

    def test_get_with_params_returns_json(self):
        payload = {"postId": 1}
        r = requests.get(
            "https://jsonplaceholder.typicode.com/comments", params=payload
        )
        self.assertEqual(len(r.json()), 5)

    def test_get_with_params_returns_json_with_expected_attributes(self):
        expected_post_id = 1
        payload = {"postId": expected_post_id}
        r = requests.get("http://jsonplaceholder.typicode.com/comments", params=payload)
        json = r.json()

        for index in range(len(json)):
            json_item = json[index]
            actual_id = json_item["postId"]
            self.assertEquals(actual_id, expected_post_id)

    def test_post_json(self):
        payload = {
            "title": "tttttiiihihihitle",
            "body": "aaaaaaaahahaha",
            "userId": 1000,
        }

        response = requests.post(
            "http://jsonplaceholder.typicode.com/posts", json=payload
        )

        self.assertEqual(response.status_code, 201)
