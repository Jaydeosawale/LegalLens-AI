import os
os.environ["DATABASE_URL"] = "sqlite://"
from unittest.mock import Mock
from api.services.storage_cleanup import queue_cleanup, complete_cleanup
from api.models.system_settings import SystemSettings
from tests.test_role_flows import RoleFlowsTest


class StorageCleanupTest(RoleFlowsTest):
    def test_task_survives_storage_failure_and_retry_clears_it(self):
        doc = Mock(filename='documents/hash/law.pdf', id='test', user_id='owner')
        identifier = queue_cleanup(self.db, doc)
        self.db.commit()
        storage = Mock()
        storage.delete_file.side_effect = RuntimeError('unavailable')
        self.assertFalse(complete_cleanup(self.db, identifier, storage))
        self.assertEqual(self.db.get(SystemSettings, identifier).values['attempts'], 1)
        storage.delete_file.side_effect = None
        self.assertTrue(complete_cleanup(self.db, identifier, storage))
        storage.delete_file.assert_called_with('documents/hash/law.pdf')
        self.assertIsNone(self.db.get(SystemSettings, identifier))

    def test_no_storage_call_for_unqueued_record(self):
        storage = Mock()
        self.assertTrue(complete_cleanup(self.db, 'r2_cleanup:missing', storage))
        storage.delete_file.assert_not_called()

    def test_cleanup_queue_rolls_back_with_database_transaction(self):
        identifier = queue_cleanup(self.db, Mock(filename='documents/hash/law.pdf', id='test', user_id='owner'))
        self.db.flush()
        self.db.rollback()
        self.assertIsNone(self.db.get(SystemSettings, identifier))

    def test_replacement_document_prevents_removing_reused_object(self):
        from api.models.document import Document
        from api.models import UserRole
        key = 'documents/hash/law.pdf'
        identifier = queue_cleanup(self.db, Mock(filename=key, id='old', user_id='owner'))
        self.db.add(Document(filename=key, original_filename='law.pdf',
                             user_id=self.users[UserRole.USER].id))
        self.db.commit()
        storage = Mock()
        self.assertFalse(complete_cleanup(self.db, identifier, storage))
        storage.delete_file.assert_not_called()
        self.assertIsNotNone(self.db.get(SystemSettings, identifier))
