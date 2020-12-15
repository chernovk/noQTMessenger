import unittest
from registration.registration import AddUser


class TestAddUser(unittest.TestCase):
    def test_add_incorrect_user_login(self):
        new = AddUser("12345678901234567890111", "1234124")
        result = new.create_user()
        self.assertEqual(result, False, "Too long username added!")
        new.__delete_user__()

    def test_add_correct_user(self):
        new = AddUser("1234567890", "1234124")
        result = new.create_user()
        self.assertEqual(result, True, "Add correct user error!")
        new.__delete_user__()

    def test_delete_user(self):
        new = AddUser("0000000000", "1")
        new.create_user()
        result = new.__delete_user__()
        self.assertEqual(result, True, "Delete user error!")

    def test_verification(self):
        new = AddUser("!1111", "1")
        result = new.verify_data()
        self.assertEqual(result, False, "Wrong character (!) added!")

        new = AddUser("1111", "344@")
        result = new.verify_data()
        self.assertEqual(result, False, "Wrong character (@) password added!")

        new = AddUser("1111", "")
        result = new.verify_data()
        self.assertEqual(result, False, "Empty password added!")

        new = AddUser("", "1")
        result = new.verify_data()
        self.assertEqual(result, False, "Empty username added!")


if __name__ == "__main__":
    unittest.main()
