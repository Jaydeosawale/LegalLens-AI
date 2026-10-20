from tests.test_role_flows import RoleFlowsTest
from api.models import UserRole
from api.routers.content_reports import router, ContentReport

class ContentReportsTest(RoleFlowsTest):
    def setUp(self):
        super().setUp()
        ContentReport.__table__.create(self.engine)
        self.app.include_router(router)

    def test_report_saved_admin_review_and_validation(self):
        payload = {"reason": "Incorrect or misleading", "content": "Synthetic test answer", "details": "Citation incorrect"}
        result = self.client.post('/content-reports', json=payload)
        self.assertEqual(result.status_code, 201)
        identifier = result.json()['id']
        self.assertEqual(self.db.get(ContentReport, identifier).user_id, self.current.id)
        self.assertEqual(self.client.get('/content-reports').status_code, 403)
        self.assertEqual(self.client.patch('/content-reports/'+identifier, json={"status":"resolved"}).status_code, 403)
        self.current = self.users[UserRole.ADMIN]
        self.assertEqual(self.client.get('/content-reports').json()[0]['details'], 'Citation incorrect')
        self.assertEqual(self.client.patch('/content-reports/'+identifier, json={"status":"resolved"}).json()['status'], 'resolved')
        self.assertEqual(self.client.post('/content-reports', json={**payload, 'content':' '*10}).status_code, 422)
        self.assertEqual(self.client.post('/content-reports', json={**payload, 'content':'a'*8001}).status_code, 422)

    def test_daily_limit(self):
        payload = {"reason": "Other", "content": "Synthetic test answer"}
        for _ in range(20):
            self.assertEqual(self.client.post('/content-reports', json=payload).status_code, 201)
        self.assertEqual(self.client.post('/content-reports', json=payload).status_code, 429)
