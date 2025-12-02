from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import messages as message_crud
from app.database import get_db

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("", response_model=List[schemas.Message])
def get_messages(
    other_user_id: Optional[int] = Query(None, description="Filter messages by conversation partner"),
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get messages for the current user"""
    return message_crud.get_messages(db, current_user.user_id, other_user_id)


@router.post("", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Send a new message"""
    return message_crud.send_message(db, current_user.user_id, payload)


@router.get("/conversations", response_model=List[schemas.Conversation])
def get_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get list of conversations"""
    return message_crud.get_conversations(db, current_user.user_id)


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get count of unread messages"""
    count = message_crud.get_unread_count(db, current_user.user_id)
    return {"unread_count": count}


@router.post("/mark-read/{sender_id}")
def mark_messages_read(
    sender_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Mark all messages from a sender as read"""
    count = message_crud.mark_messages_read(db, current_user.user_id, sender_id)
    return {"messages_marked_read": count}


@router.get("/users", response_model=List[schemas.UserListItem])
def get_available_users(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get list of users available to message"""
    return message_crud.get_available_users(db, current_user.user_id)
