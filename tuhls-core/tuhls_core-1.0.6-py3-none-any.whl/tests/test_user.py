from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):
    def test_user_fail_without_params(self):
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user()

    def test_user_fail_with_empty_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="12341234")

    def test_create_user(self):
        user = get_user_model().objects.create_user(
            email=" user@email.com ", password="user"
        )
        self.assertEqual(user.email, "user@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = get_user_model().objects.create_superuser(
            "admin@email.com  ", "admin"
        )
        self.assertEqual(admin_user.email, "admin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_str(self):
        test_user = get_user_model().objects.create_user(
            email="test@email.com", password="test"
        )
        self.assertEqual(str(test_user), "test@email.com")
