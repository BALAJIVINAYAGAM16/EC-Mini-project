from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.organization import OrganizationUpdate, OrganizationResponse

router = APIRouter(
    prefix="/organization",
    tags=["Organization"]
)


@router.get("/", response_model=OrganizationResponse)
def get_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's organization details.
    
    Returns:
        OrganizationResponse with tenant information
    
    Raises:
        HTTPException: If user has no tenant or tenant not found
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with any organization"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )
    
    return tenant


@router.put("/update", response_model=OrganizationResponse)
def update_organization(
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's organization details.
    Only admins can update organization.
    
    Args:
        org_data: Organization update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated OrganizationResponse
    
    Raises:
        HTTPException: If user is not admin, has no tenant, or update fails
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can update organization settings"
        )
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=400,
            detail="User is not associated with any organization"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )
    
    # Update only provided fields
    if org_data.organization_name:
        tenant.organization_name = org_data.organization_name
    if org_data.domain:
        tenant.domain = org_data.domain
    
    db.commit()
    db.refresh(tenant)
    
    return tenant
