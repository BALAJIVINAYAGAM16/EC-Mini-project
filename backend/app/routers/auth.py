from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role
from fastapi.security import OAuth2PasswordRequestForm
 
router = APIRouter(prefix="/auth", tags=["auth"])
 
 
 
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
   
    hashed = hash_password(user.password)
 
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_password=hashed
    )
 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
 
    return {"message": "User created"}
 
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()
 
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role
    })
 
    return {
        "access_token": token,
        "token_type": "bearer"
    }
 
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user
 
@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    user = Depends(require_role(["admin", "manager"]))
):
    users = db.query(User).filter(User.role == "employee").all()
    return users
 
 