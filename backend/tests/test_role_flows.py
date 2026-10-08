"""Exercise authorization and saved conversations against an isolated database."""
import os
import unittest
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api.database.database import Base, get_db
from api.dependencies import get_current_user
from api.models import User, UserRole, Conversation, Message, PlatformPermission
from api.routers import admin, auth, conversation, system
from api.models.system_settings import SystemSettings
from api.core.document_access import document_query
from api.models.document import Document


class RoleFlowsTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        tables = [Base.metadata.tables[name] for name in (
            "users", "chat_history", "feedback", "conversations", "messages", "platform_permissions", "documents", "system_settings", "system_events"
        )]
        Base.metadata.create_all(self.engine, tables=tables)
        self.db = Session(self.engine)
        self.users = {}
        for role, email in [(UserRole.USER, "user@example.com"), (UserRole.ADMIN, "admin@example.com"), (UserRole.SUPER_ADMIN, "owner@example.com")]:
            user = User(full_name=role.value, email=email, role=role, firebase_uid=str(uuid4()))
            self.db.add(user)
            self.users[role] = user
        self.db.add(PlatformPermission(module_name="users", enabled_for_admin=True))
        self.db.commit()
        self.current = self.users[UserRole.USER]
        self.app = FastAPI()
        for router in (admin.router, auth.router, conversation.router, system.router):
            self.app.include_router(router)
        self.app.dependency_overrides[get_db] = lambda: self.db
        self.app.dependency_overrides[get_current_user] = lambda: self.current
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.db.close()
        self.engine.dispose()

    def test_role_management_and_module_permissions(self):
        target = self.users[UserRole.USER].id
        self.assertEqual(self.client.get("/admin/users").status_code, 403)
        self.current = self.users[UserRole.ADMIN]
        self.assertEqual(self.client.get("/admin/users").status_code, 200)
        self.assertEqual(self.client.get("/auth/permissions").status_code, 200)
        self.assertEqual(self.client.put(f"/admin/users/{target}/role", json={"role": "admin"}).status_code, 403)
        self.assertEqual(self.client.put(f"/admin/users/{target}/role", json={"role": "legal_professional"}).status_code, 200)
        self.current = self.users[UserRole.SUPER_ADMIN]
        self.assertEqual(self.client.put(f"/admin/users/{target}/role", json={"role": "admin"}).status_code, 200)
        self.assertEqual(self.client.put(f"/admin/users/{target}/role", json={"role": "super_admin"}).status_code, 403)
        self.assertEqual(self.client.put(f"/admin/users/{self.current.id}/status", json={"is_active": False}).status_code, 403)
        self.client.put("/admin/platform-permissions/users", json={"enabled_for_admin": False})
        self.current = self.users[UserRole.ADMIN]
        self.assertEqual(self.client.get("/admin/users").status_code, 403)

    def test_conversations_are_private_and_persistent(self):
        c = Conversation(user_id=self.current.id, title="Saved research")
        self.db.add(c)
        self.db.flush()
        self.db.add(Message(conversation_id=c.id, role="assistant", content="Source answer", citations=[{"filename": "law.pdf", "page": 3}]))
        self.db.commit()
        identifier = str(c.id)
        self.assertEqual(len(self.client.get("/conversations/").json()), 1)
        detail = self.client.get(f"/conversations/{identifier}").json()
        self.assertEqual(detail["messages"][0]["citations"][0]["page"], 3)
        self.current = self.users[UserRole.ADMIN]
        for method in ("get", "delete"):
            self.assertEqual(getattr(self.client, method)(f"/conversations/{identifier}").status_code, 404)
        self.assertEqual(self.client.patch(f"/conversations/{identifier}", json={"title": "Other"}).status_code, 404)
        self.current = self.users[UserRole.USER]
        self.assertEqual(self.client.patch(f"/conversations/{identifier}", json={"title": "Renamed"}).json()["title"], "Renamed")
        self.assertEqual(self.client.delete(f"/conversations/{identifier}").status_code, 204)
        self.assertEqual(self.db.query(Message).count(), 0)

    def test_profile_cannot_change_role(self):
        result = self.client.patch("/auth/me", json={"full_name": "Updated Name", "role": "super_admin"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["role"], "user")
        self.assertEqual(self.client.patch("/auth/me", json={"full_name": "   "}).status_code, 422)

    def test_document_lists_are_scoped_to_the_owner(self):
        for role in (UserRole.USER, UserRole.ADMIN):
            self.db.add(Document(user_id=self.users[role].id, filename=f"{role.value}.pdf", original_filename=f"{role.value}.pdf", processing_status="completed"))
        self.db.commit()
        own = document_query(self.db, self.users[UserRole.USER]).all()
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0].user_id, self.users[UserRole.USER].id)
        self.assertEqual(document_query(self.db, self.users[UserRole.ADMIN]).count(), 2)

    def test_system_configuration_is_validated_and_admin_only(self):
        payload = {"model_name": "openai/gpt-oss-120b", "temperature": 0.2, "top_k": 10}
        self.assertEqual(self.client.put("/admin/system/settings", json=payload).status_code, 403)
        self.current = self.users[UserRole.ADMIN]
        self.assertEqual(self.client.put("/admin/system/settings", json=payload).status_code, 200)
        self.assertEqual(self.db.get(SystemSettings, "default").values["top_k"], 10)
        self.assertEqual(self.client.put("/admin/system/settings", json={**payload, "top_k": 100}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
