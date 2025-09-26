from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_user_db
from app.core.models import User
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction, made optional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_user_db)) -> Optional[User]:
    """
    Validate the token and return the current user. Returns None if no token is provided.
    For now, token is in the format 'token_{username}' (dummy implementation).
    """
    if not token:
        return None  # Return None if no token is provided, allowing optional authentication

    try:
        # Extract username from token (e.g., 'token_admin1' -> 'admin1')
        if not token.startswith("token_"):
            logger.error("Invalid token format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = token[len("token_"):]
        logger.debug(f"Extracted username from token: {username}")

        # Fetch user from database
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.error(f"User not found for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_role: str):
    """
    Dependency to ensure the current user has the required role.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if not current_user:
            logger.error("No authenticated user provided for role check")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if current_user.role != required_role:
            logger.error(f"User {current_user.username} with role {current_user.role} not authorized for role {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {current_user.role}",
            )
        return current_user
    return role_checker