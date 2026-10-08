from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from tests.test_role_flows import RoleFlowsTest
from api.models.chat_usage import ChatUsage
from api.models import UserRole
from api.services.chat_rate_limit import reserve_chat_message, get_chat_limit


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

    def test_only_super_admin_can_raise_limit_without_resetting_usage(self):
        payload = {"normal_user_daily_messages": 12}
        self.assertEqual(self.client.put("/admin/system/chat-limits", json=payload).status_code, 403)
        self.current = self.users[UserRole.ADMIN]
        self.assertEqual(self.client.put("/admin/system/chat-limits", json=payload).status_code, 403)
        user = self.users[UserRole.USER]
        for _ in range(10):
            reserve_chat_message(self.db, user)
        self.current = self.users[UserRole.SUPER_ADMIN]
        self.assertEqual(self.client.put("/admin/system/chat-limits", json=payload).status_code, 200)
        self.assertEqual(self.db.query(ChatUsage).one().message_count, 10)
        for _ in range(2):
            reserve_chat_message(self.db, user)
        with self.assertRaises(HTTPException) as caught:
            reserve_chat_message(self.db, user)
        self.assertEqual(caught.exception.status_code, 429)
        self.assertIn("12 chat messages", caught.exception.detail)
        self.client.put("/admin/system/settings", json={"model_name": "test-model", "temperature": 0, "top_k": 8})
        self.assertEqual(get_chat_limit(self.db), 12)
        for invalid in (0, 9, 1001, 10.5, "20", True):
            self.assertEqual(self.client.put("/admin/system/chat-limits", json={"normal_user_daily_messages": invalid}).status_code, 422)
