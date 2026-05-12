import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.user import User
from app.models.documents import Document
from app.models.task import Task
from app.schemas.documents import DocumentOut, DocumentCreate
from app.services.document_service import (
    create_document,
    get_document_by_id,
    get_documents_by_task,
    get_user_documents,
    delete_document,
    get_all_documents,
)
from app.services.audit_service import log_action
from app.core.logger import logger


router = APIRouter(prefix="/documents", tags=["Documents"])


def _can_access_document(document: Document, current_user: User, db: Session) -> bool:
    """Check if user can access a document"""
    if current_user.role == "admin":
        return True
    
    # User can access their own documents
    if document.uploaded_by == current_user.id:
        return True
    
    # Manager or employee can access documents attached to their tasks
    if document.task_id:
        task = db.query(Task).filter(Task.id == document.task_id).first()
        if task:
            if current_user.role == "manager" and task.created_by_id == current_user.id:
                return True
            if task.assigned_to_id == current_user.id:
                return True
    
    return False


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    task_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document
    
    - **file**: The file to upload (required)
    - **task_id**: Optional task ID to attach the document to
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name"
            )
        
        # Check file size (max 50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Create document
        document = create_document(db, file, current_user.id, task_id)
        
        # Log audit
        log_action(
            db,
            current_user.id,
            "upload",
            "document",
            document.id
        )
        
        logger.info(f"User {current_user.id} uploaded document {document.id}")
        return document
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document details"""
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not _can_access_document(document, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a document file"""
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not _can_access_document(document, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Log audit
    log_action(
        db,
        current_user.id,
        "download",
        "document",
        document.id
    )
    
    logger.info(f"User {current_user.id} downloaded document {document.id}")
    
    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type="application/octet-stream"
    )


@router.get("/task/{task_id}", response_model=list[DocumentOut])
def get_task_documents(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all documents for a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check access to task
    if current_user.role != "admin":
        if current_user.role == "manager" and task.created_by_id != current_user.id:
            if task.assigned_to_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "employee":
            if task.assigned_to_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
    
    return get_documents_by_task(db, task_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doc(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    """Delete a document"""
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Only admin or the uploader can delete
    if current_user.role != "admin" and document.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' documents"
        )
    
    delete_document(db, document_id)
    
    # Log audit
    log_action(
        db,
        current_user.id,
        "delete",
        "document",
        document_id
    )
    
    logger.info(f"User {current_user.id} deleted document {document_id}")


@router.get("/", response_model=list[DocumentOut])
def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List documents with pagination"""
    if current_user.role == "admin":
        documents, total = get_all_documents(db, limit=limit, offset=skip)
        return documents
    else:
        # Regular users see only their own documents
        return get_user_documents(db, current_user.id)
