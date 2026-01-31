"""
Authentication routes for registration, login, and user info
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import User, UserRole, Offerer
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user with email and password.
    Creates Offerer profile if registering as offerer.
    Returns JWT access token on success.
    """
    # Check if user already exists
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate offerer has company
    if request.role == UserRole.OFFERER and not request.company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name is required for offerer registration"
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        role=request.role,
        is_active=True
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create Offerer profile if registering as offerer
    if request.role == UserRole.OFFERER:
        offerer = Offerer(
            email=new_user.email,
            company=request.company
        )
        session.add(offerer)
        session.commit()

    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login with email and password.
    Returns JWT access token on success.
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )
