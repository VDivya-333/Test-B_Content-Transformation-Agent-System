from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, List
from app.utils.logger import get_logger
from app.utils.limiter import limiter
from app.config.settings import settings

logger = get_logger()

# Configuration - In production, these should be in environment variables
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a JWT token for a specific user."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error encoding JWT: {e}")
        return None

def decode_access_token(token: str):
    """Decodes and validates a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        return None

reusable_bearer = HTTPBearer()

def require_role(allowed_roles: Union[str, List[str]]):
    """Dependency that checks for a required role in the JWT token."""
    async def role_checker(token: str = Depends(reusable_bearer)):
        payload = decode_access_token(token.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        role = payload.get("role")
        required_list = [allowed_roles] if isinstance(allowed_roles, str) else allowed_roles
        
        if role not in required_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have enough permissions. Requires one of: {required_list}",
            )
        return payload
    return role_checker

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: LoginRequest
):
    if login_data.username == "admin" and login_data.password == "password123":
        token = create_access_token(data={"sub": login_data.username, "role": "admin"})
        if not token:
            raise HTTPException(status_code=500, detail="Could not generate access token")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
