from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from tests.test_role_flows import RoleFlowsTest
from api.models.chat_usage import ChatUsage
from api.models import UserRole
from api.services.chat_rate_limit import reserve_chat_message


class ChatRateLimitTest(RoleFlowsTest):
    def setUp(self):
        super().setUp()
        ChatUsage.__table__.create(self.engine)

    def test_tenth_allowed_eleventh_blocked_and_next_day_resets(self):
        now = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
        user = self.users[UserRole.USER]
        for _ in range(10):
            reserve_chat_message(self.db, user, now)
        with self.assertRaises(HTTPException) as caught:
            reserve_chat_message(self.db, user, now)
        self.assertEqual(caught.exception.status_code, 429)
        self.assertEqual(caught.exception.headers["Retry-After"], "43200")
        self.assertEqual(self.db.query(ChatUsage).one().message_count, 10)
        reserve_chat_message(self.db, user, now + timedelta(days=1))
        self.assertEqual(self.db.query(ChatUsage).count(), 2)

    def test_administrators_are_exempt(self):
        for role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            for _ in range(11):
                reserve_chat_message(self.db, self.users[role])
        self.assertEqual(self.db.query(ChatUsage).count(), 0)
