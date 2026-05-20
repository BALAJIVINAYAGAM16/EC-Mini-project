from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import stripe
from app.core.config import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES, STRIPE_SECRET_KEY
from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    hash_password,
    hash_token,
    is_valid_bcrypt_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.subcription import Subscription
from app.schemas.token import PasswordResetConfirm, PasswordResetRequest, RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserOut

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db_user: User, db: Session) -> Token:
    access_token = create_access_token({"user_id": db_user.id, "role": db_user.role})
    refresh_token, expires_at = create_refresh_token()
    db_user.refresh_token_hash = hash_token(refresh_token)
    db_user.refresh_token_expires_at = expires_at
    db.commit()
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        # Create a tenant for the user
        tenant = Tenant(
            organization_name=user.name,
            domain=user.email.split("@")[1]
        )
        db.add(tenant)
        db.flush()  # Flush to get the tenant ID without committing
        
        # Create a Stripe customer
        stripe_customer = stripe.Customer.create(email=user.email)
        
        # Create a subscription for the tenant
        subscription = Subscription(
            tenant_id=tenant.id,
            plan="Basic",
            credits=100,
            stripe_customer_id=stripe_customer.id
        )
        db.add(subscription)
        db.flush()
        
        # Create the user with tenant_id
        new_user = User(
            name=user.name,
            email=user.email,
            role=user.role.value,
            hashed_password=hash_password(user.password),
            tenant_id=tenant.id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except stripe.error.StripeError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating Stripe customer: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during registration: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    return _issue_tokens(db_user, db)


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    db_user = db.query(User).filter(User.refresh_token_hash == token_hash).first()
    if (
        not db_user
        or not db_user.is_active
        or not db_user.refresh_token_expires_at
        or db_user.refresh_token_expires_at <= datetime.utcnow()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return _issue_tokens(db_user, db)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.refresh_token_hash = None
    current_user.refresh_token_expires_at = None
    db.commit()
    return {"message": "Logged out"}


@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == payload.email).first()
    if not db_user:
        return {"message": "If that email exists, a reset link has been generated."}

    reset_token, expires_at = create_password_reset_token(PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    db_user.password_reset_token_hash = hash_token(reset_token)
    db_user.password_reset_expires_at = expires_at
    db.commit()

    return {
        "message": "Password reset token generated.",
        "reset_token": reset_token,
        "expires_at": expires_at,
    }


@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    if not is_valid_bcrypt_password(payload.new_password) or len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be between 6 and 72 bytes.",
        )

    token_hash = hash_token(payload.token)
    db_user = db.query(User).filter(User.password_reset_token_hash == token_hash).first()
    if (
        not db_user
        or not db_user.password_reset_expires_at
        or db_user.password_reset_expires_at <= datetime.utcnow()
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    db_user.hashed_password = hash_password(payload.new_password)
    db_user.password_reset_token_hash = None
    db_user.password_reset_expires_at = None
    db_user.refresh_token_hash = None
    db_user.refresh_token_expires_at = None
    db.commit()

    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
