"""Bounded retrieval and embedding lifecycle regression tests."""
import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
from sqlalchemy.dialects import postgresql
from api.services.postgres_bm25 import PostgresBM25Retriever
from api.services.conversation_service import ConversationService
from rag.embeddings.embeddings import EmbeddingModel
from tests.test_document_review import DocumentReviewTest
from api.models.role import UserRole


class KeywordMemoryTest(DocumentReviewTest):
    def test_keyword_query_is_bounded_and_access_filtered(self):
        doc = self.document(UserRole.ADMIN)
        statement = PostgresBM25Retriever.search_statement(
            self.db, 'contract termination', 500, self.users[UserRole.USER].id, [doc.id])
        compiled = statement.compile(dialect=postgresql.dialect())
        sql = str(compiled)
        self.assertIn('LIMIT', sql)
        self.assertIn(50, compiled.params.values())
        self.assertIn('ts_rank_cd', sql)
        self.assertIn('documents.approval_status', sql)
        self.assertIn('documents.access_enabled', sql)
        self.assertIn('documents.user_id', sql)
        self.assertIn('documents.rag_scope', sql)

    def test_empty_query_does_not_open_database(self):
        with patch('api.services.postgres_bm25.SessionLocal') as session:
            self.assertEqual(PostgresBM25Retriever.retrieve('!!!', user_id='test'), [])
        session.assert_not_called()


class EmbeddingMemoryTest(unittest.TestCase):
    def test_free_tier_preserves_source_text_without_compression_calls(self):
        from rag.retrievers.context_compressor import ContextCompressor
        documents = [Mock(page_content='Original legal source')]
        with patch.dict(os.environ, {'CONTEXT_COMPRESSION_ENABLED': 'false'}), \
                patch('rag.retrievers.context_compressor.LLMService.get_llm') as llm:
            self.assertIs(ContextCompressor.compress('question', documents), documents)
        llm.assert_not_called()

    def test_chat_history_fetches_only_recent_messages_in_order(self):
        db = Mock()
        query = db.query.return_value.filter.return_value.order_by.return_value
        query.limit.return_value.all.return_value = ['newest', 'older']
        self.assertEqual(ConversationService.get_messages(db, 'conversation', limit=20), ['older', 'newest'])
        query.limit.assert_called_once_with(20)

    def test_query_releases_model_on_success_and_failure(self):
        for failure in (False, True):
            model = Mock()
            model.embed_query.side_effect = RuntimeError('failed') if failure else None
            model.embed_query.return_value = [0.1] * 384
            with patch.object(EmbeddingModel, 'get_model', return_value=model), \
                    patch.object(EmbeddingModel, 'release_model') as release:
                if failure:
                    with self.assertRaises(RuntimeError):
                        EmbeddingModel.embed_query('question')
                else:
                    self.assertEqual(len(EmbeddingModel.embed_query('question')), 384)
                release.assert_called_once()
