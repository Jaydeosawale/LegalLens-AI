import os
import shutil
import tempfile
import traceback

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.dependencies import get_current_user
from api.models.chat_history import ChatHistory
from api.models.document import Document
from api.core.document_access import document_query
from uuid import UUID
import json
from api.routers.auth import get_user_preferences
from api.models.role import UserRole
from api.models.user import User
from api.schemas.chat import ChatResponse
from api.services.conversation_service import ConversationService
from api.services.rag_chain import RAGChain
from api.services.chat_rate_limit import reserve_chat_message
from api.llm.llm import public_ai_error

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

# ============================================================
# Global Vector Database
# ============================================================

# ============================================================
# Health
# ============================================================

@router.get("/")
def chat_home():

    return {
        "message": "Chat API Working"
    }


# ============================================================
# Multimodal Chat
# ============================================================

@router.post(
    "/",
    response_model=ChatResponse,
)
def chat(

    question: str = Form(..., min_length=1, max_length=2000),

    conversation_id: str | None = Form(None),
    document_ids: str | None = Form(None),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    temp_image_path = None

    try:
        selected_ids = None
        if document_ids:
            try:
                parsed = json.loads(document_ids)
                if not isinstance(parsed, list) or not 1 <= len(parsed) <= 10:
                    raise ValueError()
                selected_ids = [str(UUID(value)) for value in parsed]
            except (ValueError, TypeError):
                raise HTTPException(422, "Select between one and ten valid documents.")
            allowed = document_query(db, current_user).filter(Document.id.in_(selected_ids)).all()
            if len(allowed) != len(set(selected_ids)):
                raise HTTPException(404, "Document not found.")
            if any(document.approval_status != 'approved' or not document.access_enabled for document in allowed):
                raise HTTPException(409, "Selected documents are awaiting approval or have been disabled.")

        if conversation_id is not None and ConversationService.get_conversation(
            db=db, conversation_id=conversation_id, user_id=current_user.id
        ) is None:
            raise HTTPException(404, "Conversation not found.")
        reserve_chat_message(db, current_user)

        # =====================================================
        # Save Uploaded Image
        # =====================================================

        if image is not None:

            suffix = os.path.splitext(
                image.filename
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:

                shutil.copyfileobj(
                    image.file,
                    temp_file,
                )

                temp_image_path = temp_file.name

            print("=" * 80)
            print("Uploaded Image")
            print(temp_image_path)
            print("=" * 80)

        # =====================================================
        # Conversation
        # =====================================================

        if conversation_id is None:

            conversation = ConversationService.create_conversation(

                db=db,

                user_id=current_user.id,

                title=ConversationService.generate_title(
                    question
                ),

            )

            conversation_id = conversation.id

        else:

            conversation = ConversationService.get_conversation(

                db=db,

                conversation_id=conversation_id,

                user_id=current_user.id,

            )

            if conversation is None:

                raise HTTPException(

                    status_code=404,

                    detail="Conversation not found.",

                )

        # =====================================================
        # Memory
        # =====================================================

        history = []

        previous_messages = ConversationService.get_messages(

            db=db,

            conversation_id=conversation_id,
            limit=20,

        )

        for msg in previous_messages:

            if msg.role == "user":

                history.append(
                    HumanMessage(
                        content=msg.content
                    )
                )

            else:

                history.append(
                    AIMessage(
                        content=msg.content
                    )
                )
                        # =====================================================
        # Ask Multimodal RAG
        # =====================================================

        result = RAGChain.ask(
            user_id=current_user.id,
            document_ids=selected_ids,
            preferences=get_user_preferences(db, current_user),

            question=question,

            memory=history,

            uploaded_image=temp_image_path,

        )

        if result is None:

            raise HTTPException(

                status_code=500,

                detail="Unable to generate response.",

            )

        answer = result.get(
            "answer",
            "",
        )


        citations = result.get(
            "citations",
            [],
        )

        raw_documents = result.get(
            "documents",
            [],
        )

        images = result.get(
            "images",
            [],
        )

        similar_images = result.get(
            "similar_images",
            [],
        )

        image_analysis = result.get(
            "image_analysis",
            None,
        )

        # =====================================================
        # Save User Message
        # =====================================================

        ConversationService.add_message(

            db=db,

            conversation_id=conversation_id,

            role="user",

            content=question,

        )

        # =====================================================
        # Save Assistant Message
        # =====================================================

        ConversationService.add_message(

            db=db,

            conversation_id=conversation_id,

            role="assistant",

            content=answer,

            citations=citations,

            documents=[],

            images=images,

        )

        # =====================================================
        # PDF Names
        # =====================================================

        pdf_names = sorted(

            {

                doc.metadata.get(
                    "filename",
                    "Unknown",
                )

                for doc in raw_documents

            }

        )

        # =====================================================
        # Chat History
        # =====================================================

        chat_history = ChatHistory(

            user_id=current_user.id,

            question=question,

            answer=answer,

            pdf_name=", ".join(pdf_names),

        )

        db.add(chat_history)

        db.commit()

        db.refresh(chat_history)

        # =====================================================
        # Convert LangChain Documents
        # =====================================================

        documents = []

        for doc in raw_documents:

            documents.append(

                {

                    "page_content": doc.page_content,

                    "metadata": {

                        "filename": doc.metadata.get(
                            "filename",
                            "Unknown",
                        ),

                        "page": doc.metadata.get(
                            "page",
                            0,
                        ),

                        "chunk_id": doc.metadata.get(
                            "chunk_id",
                            0,
                        ),

                    },

                }

            )
                    # =====================================================
        # Build Response
        # =====================================================

        response = {

            "chat_id": str(chat_history.id),

            "conversation_id": str(conversation_id),

            "answer": answer,

            "citations": citations,

            "images": images,

            "similar_images": similar_images,

            "image_analysis": image_analysis,

        }

        # =====================================================
        # Admin Response
        # =====================================================

        if current_user.role in (

            UserRole.ADMIN,

            UserRole.SUPER_ADMIN,

        ):

            response["documents"] = documents

            response["images"] = images

            response["similar_images"] = similar_images

            response["image_analysis"] = image_analysis

        # =====================================================
        # Cleanup Uploaded Image
        # =====================================================

        if temp_image_path is not None:

            try:

                if os.path.exists(temp_image_path):

                    os.remove(temp_image_path)

            except Exception as cleanup_error:

                print(
                    "Image cleanup failed:",
                    cleanup_error,
                )

        # =====================================================
        # Success Logs
        # =====================================================

        print("\n" + "=" * 80)

        print("CHAT REQUEST COMPLETED")

        print("=" * 80)

        print("Conversation ID    :", conversation_id)

        print("Documents          :", len(documents))

        print("Images             :", len(images))

        print("Similar Images     :", len(similar_images))

        print(
            "Image Uploaded     :",
            temp_image_path is not None,
        )

        print(
            "Image Analysis     :",
            image_analysis is not None,
        )

        print("=" * 80)

        return ChatResponse(

            **response

        )

    # =====================================================
    # HTTP Exceptions
    # =====================================================

    except HTTPException:

        if temp_image_path and os.path.exists(temp_image_path):

            try:

                os.remove(temp_image_path)

            except Exception:

                pass

        raise

    # =====================================================
    # Unexpected Exceptions
    # =====================================================

    except Exception as e:

        traceback.print_exc()

        db.rollback()

        if temp_image_path and os.path.exists(temp_image_path):

            try:

                os.remove(temp_image_path)

            except Exception:

                pass

        ai_error = public_ai_error(e)
        if ai_error is not None:
            raise ai_error from None

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )
