import unittest
from reg.registration import AddUser


class TestAddUser(unittest.TestCase):
    def test_add_incorrect_user(self):
        new = AddUser("123456789012345678901", "1234124", "1")
        result = new.create_user()
        self.assertEqual(result, False)

    def test_add_correct_user(self):
        new = AddUser("1234567890", "1234124", "1")
        result = new.create_user()
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
