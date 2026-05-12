import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import UploadFile

from app.models.documents import Document
from app.models.task import Task
from app.core.logger import logger


UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(upload_file: UploadFile, user_id: int, task_id: int = None) -> str:
    """Save uploaded file and return file path"""
    try:
        # Create directory for the user
        user_dir = UPLOAD_DIR / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(upload_file.filename).suffix
        unique_filename = f"{timestamp}_{upload_file.filename}"
        
        file_path = user_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"File saved: {file_path} by user {user_id}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def create_document(db: Session, upload_file: UploadFile, user_id: int, task_id: int = None) -> Document:
    """Create a new document record in the database"""
    file_path = save_uploaded_file(upload_file, user_id, task_id)
    
    # Check if task exists
    if task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
    
    document = Document(
        file_name=upload_file.filename,
        file_path=file_path,
        version=1,
        uploaded_by=user_id,
        task_id=task_id,
        created_at=datetime.utcnow()
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(f"Document created: {document.id} - {upload_file.filename}")
    return document


def get_document_by_id(db: Session, document_id: int) -> Document:
    """Get document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents_by_task(db: Session, task_id: int) -> list[Document]:
    """Get all documents for a specific task"""
    return (
        db.query(Document)
        .filter(Document.task_id == task_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_user_documents(db: Session, user_id: int) -> list[Document]:
    """Get all documents uploaded by a user"""
    return (
        db.query(Document)
        .filter(Document.uploaded_by == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document_versions(db: Session, file_name: str) -> list[Document]:
    """Get all versions of a document by file name"""
    return (
        db.query(Document)
        .filter(Document.file_name == file_name)
        .order_by(Document.version.desc())
        .all()
    )


def increment_version(db: Session, file_name: str) -> int:
    """Get next version number for a file"""
    latest = (
        db.query(func.max(Document.version))
        .filter(Document.file_name == file_name)
        .scalar()
    )
    return (latest or 0) + 1


def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document and its file"""
    document = get_document_by_id(db, document_id)
    if not document:
        return False
    
    try:
        # Delete file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
            logger.info(f"File deleted: {document.file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
    
    # Delete database record
    db.delete(document)
    db.commit()
    logger.info(f"Document deleted: {document_id}")
    return True


def get_all_documents(db: Session, limit: int = 100, offset: int = 0) -> tuple[list[Document], int]:
    """Get all documents with pagination"""
    query = db.query(Document).order_by(Document.created_at.desc())
    total = query.count()
    documents = query.limit(limit).offset(offset).all()
    return documents, total
