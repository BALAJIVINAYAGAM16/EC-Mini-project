# routers/document_router.py

from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_role
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.documents import DocumentOut

from app.services.document_service import (
    upload_document_service,
    get_document_service,
    download_document_service,
    get_task_documents_service,
    delete_document_service,
    list_documents_service,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile = File(...),
    task_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await upload_document_service(
        db,
        file,
        task_id,
        current_user
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_document_service(
        db,
        document_id,
        current_user
    )


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return download_document_service(
        db,
        document_id,
        current_user
    )


@router.get("/task/{task_id}", response_model=list[DocumentOut])
def get_task_documents(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_documents_service(
        db,
        task_id,
        current_user
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_doc(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "manager"])
    ),
):
    return delete_document_service(
        db,
        document_id,
        current_user
    )


@router.get("/", response_model=list[DocumentOut])
def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_documents_service(
        db,
        current_user,
        skip,
        limit
    )