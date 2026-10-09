"""Verify RAG approval and private/shared document boundaries."""
from unittest.mock import patch, Mock
from types import SimpleNamespace
import hashlib
import os
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from api.models.document_chunk import DocumentChunk
from api.models.document_embedding import DocumentEmbedding
from api.core.document_access import rag_document_query, document_query
from api.services.document_review_service import review_document
from api.models.document import Document
from api.models import UserRole
from tests.test_role_flows import RoleFlowsTest


@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kwargs):
    return "JSON"


class DocumentReviewTest(RoleFlowsTest):
    def setUp(self):
        super().setUp()
        DocumentChunk.__table__.create(self.engine)
        DocumentEmbedding.__table__.create(self.engine)

    def document(self, role, status="pending"):
        doc = Document(user_id=self.users[role].id, filename="test.pdf",
                       original_filename="test.pdf", processing_status="completed",
                       approval_status=status, submitted_by=self.users[UserRole.ADMIN].id)
        self.db.add(doc)
        self.db.flush()
        self.db.add(DocumentChunk(document_id=doc.id, chunk_index=0, content="Legal clause"))
        self.db.commit()
        return doc

    def approve(self, doc, scope="private"):
        with patch("api.services.document_review_service.EmbeddingModel.get_model",
                   return_value=Mock(embed_documents=Mock(return_value=[[0.1] * 384]))):
            return review_document(self.db, doc, self.users[UserRole.SUPER_ADMIN], "approved", scope, None)

    def test_only_super_admin_can_approve(self):
        doc = self.document(UserRole.USER)
        for role in (UserRole.USER, UserRole.ADMIN):
            with self.assertRaises(HTTPException) as caught:
                review_document(self.db, doc, self.users[role], "approved", "private", None)
            self.assertEqual(caught.exception.status_code, 403)
        doc.approval_status = "draft"
        with self.assertRaises(HTTPException) as caught:
            self.approve(doc)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.query(DocumentEmbedding).count(), 0)

    def test_private_approval_and_revocation(self):
        doc = self.document(UserRole.USER)
        uid = self.users[UserRole.USER].id
        self.assertEqual(rag_document_query(self.db, uid).count(), 0)
        self.approve(doc)
        self.assertEqual(self.db.query(DocumentEmbedding).count(), 1)
        self.assertEqual(rag_document_query(self.db, uid).count(), 1)
        self.assertEqual(rag_document_query(self.db, self.users[UserRole.ADMIN].id, [doc.id]).count(), 0)
        doc.access_enabled = False
        self.db.commit()
        self.assertEqual(rag_document_query(self.db, uid, [doc.id]).count(), 0)
        review_document(self.db, doc, self.users[UserRole.SUPER_ADMIN], "rejected", "private", "Revoked")
        self.assertEqual(self.db.query(DocumentEmbedding).count(), 0)

    def test_shared_knowledge_does_not_expand_user_document_list(self):
        doc = self.document(UserRole.ADMIN)
        self.approve(doc, "shared")
        user = self.users[UserRole.USER]
        self.assertEqual(rag_document_query(self.db, user.id).count(), 1)
        self.assertEqual(document_query(self.db, user).count(), 0)
        personal = self.document(UserRole.USER)
        with self.assertRaises(HTTPException) as caught:
            self.approve(personal, "shared")
        self.assertEqual(caught.exception.status_code, 422)

    def test_approval_indexes_chunks_in_bounded_batches(self):
        doc = self.document(UserRole.ADMIN)
        for index in range(1, 19):
            self.db.add(DocumentChunk(document_id=doc.id, chunk_index=index, content=f"Clause {index}"))
        self.db.commit()
        embed = Mock(side_effect=lambda texts: [[0.1] * 384 for _ in texts])
        with patch("api.services.document_review_service.EmbeddingModel.get_model",
                   return_value=Mock(embed_documents=embed)):
            with patch("api.services.document_review_service.EmbeddingModel.release_model") as release:
                review_document(self.db, doc, self.users[UserRole.SUPER_ADMIN], "approved", "shared", None)
        release.assert_called_once()
        self.assertEqual(self.db.query(DocumentEmbedding).count(), 19)
        self.assertEqual([len(call.args[0]) for call in embed.call_args_list], [8, 8, 3])

    def test_failed_indexing_releases_embedding_model(self):
        doc = self.document(UserRole.ADMIN)
        with patch("api.services.document_review_service.EmbeddingModel.get_model",
                   return_value=Mock(embed_documents=Mock(side_effect=RuntimeError("Indexing failed")))):
            with patch("api.services.document_review_service.EmbeddingModel.release_model") as release:
                with self.assertRaises(RuntimeError):
                    review_document(self.db, doc, self.users[UserRole.SUPER_ADMIN], "approved", "shared", None)
        release.assert_called_once()

    def test_precomputed_embeddings_require_matching_chunk_text(self):
        doc = self.document(UserRole.ADMIN)
        supplied = [SimpleNamespace(chunk_index=0,
                                    content_sha256=hashlib.sha256(b'Legal clause').hexdigest(),
                                    embedding=[0.1] * 384)]
        with patch("api.services.document_review_service.EmbeddingModel.get_model") as get_model:
            review_document(self.db, doc, self.users[UserRole.SUPER_ADMIN],
                            "approved", "shared", None, supplied)
        get_model.assert_not_called()
        self.assertEqual(self.db.query(DocumentEmbedding).count(), 1)

        other = self.document(UserRole.ADMIN)
        supplied[0].content_sha256 = "0" * 64
        with self.assertRaises(HTTPException) as caught:
            review_document(self.db, other, self.users[UserRole.SUPER_ADMIN],
                            "approved", "shared", None, supplied)
        self.assertEqual(caught.exception.status_code, 422)
        self.db.rollback()
        self.assertEqual(other.approval_status, "pending")
