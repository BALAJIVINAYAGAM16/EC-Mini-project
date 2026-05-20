# services/document_service.py

import os
import shutil

from datetime import datetime
from pathlib import Path

from fastapi import (
    HTTPException,
    UploadFile,
    status
)
from fastapi.responses import FileResponse

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.documents import Document
from app.models.task import Task
from app.models.user import User

from app.services.audit_service import log_action


UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =====================================
# HELPERS
# =====================================

def can_access_document(
    document: Document,
    current_user: User,
    db: Session
) -> bool:

    if current_user.role == "admin":
        return True

    if document.uploaded_by == current_user.id:
        return True

    if document.task_id:
        task = (
            db.query(Task)
            .filter(Task.id == document.task_id)
            .first()
        )

        if task:
            if (
                current_user.role == "manager"
                and task.created_by_id == current_user.id
            ):
                return True

            if task.assigned_to_id == current_user.id:
                return True

    return False


def save_uploaded_file(
    upload_file: UploadFile,
    user_id: int
) -> str:

    try:
        user_dir = UPLOAD_DIR / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        unique_filename = (
            f"{timestamp}_{upload_file.filename}"
        )

        file_path = user_dir / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                upload_file.file,
                buffer
            )

        logger.info(f"File saved: {file_path}")

        return str(file_path)

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def get_next_document_version(
    db: Session,
    file_name: str,
    task_id: int = None
):

    query = (
        db.query(func.max(Document.version))
        .filter(Document.file_name == file_name)
    )

    if task_id is None:
        query = query.filter(
            Document.task_id.is_(None)
        )
    else:
        query = query.filter(
            Document.task_id == task_id
        )

    latest = query.scalar()

    return (latest or 0) + 1


# =====================================
# CORE CRUD
# =====================================

def create_document(
    db: Session,
    upload_file: UploadFile,
    user_id: int,
    task_id: int = None
):

    if task_id:
        task = (
            db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise ValueError(
                f"Task {task_id} not found"
            )

    file_path = save_uploaded_file(
        upload_file,
        user_id
    )

    document = Document(
        file_name=upload_file.filename,
        file_path=file_path,
        version=get_next_document_version(
            db,
            upload_file.filename,
            task_id
        ),
        uploaded_by=user_id,
        task_id=task_id,
        created_at=datetime.utcnow()
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(
        f"Document created: {document.id}"
    )

    return document


def get_document_by_id(
    db: Session,
    document_id: int
):

    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def get_documents_by_task(
    db: Session,
    task_id: int
):

    return (
        db.query(Document)
        .filter(Document.task_id == task_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_user_documents(
    db: Session,
    user_id: int
):

    return (
        db.query(Document)
        .filter(Document.uploaded_by == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_all_documents(
    db: Session,
    limit: int = 100,
    offset: int = 0
):

    query = (
        db.query(Document)
        .order_by(Document.created_at.desc())
    )

    total = query.count()

    documents = (
        query.limit(limit)
        .offset(offset)
        .all()
    )

    return documents, total


def delete_document(
    db: Session,
    document_id: int
):

    document = get_document_by_id(
        db,
        document_id
    )

    if not document:
        return False

    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

    except Exception as e:
        logger.error(
            f"Error deleting file: {str(e)}"
        )

    db.delete(document)
    db.commit()

    logger.info(
        f"Document deleted: {document_id}"
    )

    return True


# =====================================
# ROUTER SERVICES
# =====================================

async def upload_document_service(
    db: Session,
    file: UploadFile,
    task_id: int,
    current_user: User
):

    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name"
            )

        MAX_FILE_SIZE = 50 * 1024 * 1024

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )

        await file.seek(0)

        document = create_document(
            db,
            file,
            current_user.id,
            task_id
        )

        log_action(
            db,
            current_user.id,
            "upload",
            "document",
            document.id
        )

        logger.info(
            f"User {current_user.id} uploaded document {document.id}"
        )

        return document

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(
            f"Upload error: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )


def get_document_service(
    db: Session,
    document_id: int,
    current_user: User
):

    document = get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not can_access_document(
        document,
        current_user,
        db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return document


def download_document_service(
    db: Session,
    document_id: int,
    current_user: User
):

    document = get_document_service(
        db,
        document_id,
        current_user
    )

    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    log_action(
        db,
        current_user.id,
        "download",
        "document",
        document.id
    )

    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type="application/octet-stream"
    )


def get_task_documents_service(
    db: Session,
    task_id: int,
    current_user: User
):

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if current_user.role != "admin":

        if (
            current_user.role == "manager"
            and task.created_by_id != current_user.id
            and task.assigned_to_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        if (
            current_user.role == "employee"
            and task.assigned_to_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return get_documents_by_task(
        db,
        task_id
    )


def delete_document_service(
    db: Session,
    document_id: int,
    current_user: User
):

    document = get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if (
        current_user.role != "admin"
        and document.uploaded_by != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users documents"
        )

    delete_document(
        db,
        document_id
    )

    log_action(
        db,
        current_user.id,
        "delete",
        "document",
        document_id
    )

    logger.info(
        f"User {current_user.id} deleted document {document_id}"
    )

    return None


def list_documents_service(
    db: Session,
    current_user: User,
    skip: int,
    limit: int
):

    if current_user.role == "admin":
        documents, _ = get_all_documents(
            db,
            limit,
            skip
        )

        return documents

    return get_user_documents(
        db,
        current_user.id
    )