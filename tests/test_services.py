import unittest
from uuid import uuid4

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.data_access import DataAccess
from app.models.user import User
from app.schemas.user import UserStatusChange
from app.schemas.user import UserCreate
from app.services.access_service import add_access, get_access_step1, get_access_step2, validate_token
from app.services.query_service import get_user_details
from app.services.user_service import add_user, change_status


class ServiceFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        init_db()

    def setUp(self) -> None:
        self.db = SessionLocal()
        self.db.query(DataAccess).delete()
        self.db.query(User).delete()
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()

    def _email(self) -> str:
        return f"user_{uuid4().hex[:10]}@example.com"

    def test_add_user_and_duplicate_rejected(self) -> None:
        email = self._email()
        add_user(self.db, UserCreate(name="Alice", email=email, data1="a", data2="b"))
        with self.assertRaises(ValueError):
            add_user(self.db, UserCreate(name="Alice2", email=email, data1="a", data2="b"))

    def test_disabled_user_cannot_get_token(self) -> None:
        email = self._email()
        user = add_user(self.db, UserCreate(name="Bob", email=email, data1="d1", data2="d2"))
        change_status(self.db, UserStatusChange(email=user.email, status_enabled=False))

        with self.assertRaises(PermissionError):
            add_access(self.db, email)

    def test_otp_flow_returns_token(self) -> None:
        email = self._email()
        add_user(self.db, UserCreate(name="Carol", email=email, data1="x", data2="y"))
        access = get_access_step1(self.db, email)
        self.assertIsNotNone(access.otp_code)
        self.assertTrue((access.otp_code or "").isdigit())
        self.assertEqual(len(access.otp_code or ""), 6)
        final = get_access_step2(self.db, email, access.otp_code or "")
        self.assertTrue(bool(final.auth_token))

    def test_validate_token_and_filtered_query(self) -> None:
        email_a = self._email()
        email_b = self._email()
        add_user(self.db, UserCreate(name="Adam", email=email_a, data1="x1", data2="y1"))
        add_user(self.db, UserCreate(name="Brian", email=email_b, data1="x2", data2="y2"))
        access = add_access(self.db, email_a)
        self.assertTrue(bool(access.auth_token))
        validate_token(self.db, access.auth_token or "")

        rows = get_user_details(self.db, field_name="name", name_prefix="A", limit=10, offset=0)
        self.assertGreaterEqual(len(rows), 1)
        self.assertIn("name", rows[0])


if __name__ == "__main__":
    unittest.main()
