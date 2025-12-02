from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from app import models, schemas


def _get_user_full_name(db: Session, user_id: int) -> str:
    """Get full name for any user type"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        return "Unknown User"
    
    if user.role == "student":
        student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
        if student:
            return " ".join(filter(None, [student.fname, student.mname, student.lname]))
    elif user.role == "lecturer":
        lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == user_id).first()
        if lecturer:
            return " ".join(filter(None, [lecturer.title, lecturer.fname, lecturer.mname, lecturer.lname]))
    elif user.role == "manager":
        manager = db.query(models.Manager).filter(models.Manager.user_id == user_id).first()
        if manager:
            return manager.name
    
    return user.username or user.email


def get_messages(db: Session, user_id: int, other_user_id: Optional[int] = None) -> List[schemas.Message]:
    """Get messages for a user, optionally filtered by conversation partner"""
    query = db.query(models.Message).filter(
        or_(
            models.Message.sender_id == user_id,
            models.Message.receiver_id == user_id
        )
    )
    
    if other_user_id:
        query = query.filter(
            or_(
                and_(models.Message.sender_id == user_id, models.Message.receiver_id == other_user_id),
                and_(models.Message.sender_id == other_user_id, models.Message.receiver_id == user_id)
            )
        )
    
    messages = query.order_by(models.Message.created_at.desc()).all()
    
    result = []
    for msg in messages:
        result.append(schemas.Message(
            id=msg.message_id,
            sender_id=msg.sender_id,
            sender_name=_get_user_full_name(db, msg.sender_id),
            receiver_id=msg.receiver_id,
            receiver_name=_get_user_full_name(db, msg.receiver_id),
            content=msg.content,
            is_read=msg.is_read or False,
            created_at=msg.created_at or datetime.utcnow()
        ))
    
    return result


def send_message(db: Session, sender_id: int, payload: schemas.MessageCreate) -> schemas.Message:
    """Send a new message"""
    message = models.Message(
        sender_id=sender_id,
        receiver_id=payload.receiver_id,
        content=payload.content,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return schemas.Message(
        id=message.message_id,
        sender_id=message.sender_id,
        sender_name=_get_user_full_name(db, message.sender_id),
        receiver_id=message.receiver_id,
        receiver_name=_get_user_full_name(db, message.receiver_id),
        content=message.content,
        is_read=message.is_read or False,
        created_at=message.created_at or datetime.utcnow()
    )


def mark_messages_read(db: Session, user_id: int, sender_id: int) -> int:
    """Mark all messages from a sender as read"""
    updated = db.query(models.Message).filter(
        models.Message.receiver_id == user_id,
        models.Message.sender_id == sender_id,
        models.Message.is_read == False
    ).update({models.Message.is_read: True})
    
    db.commit()
    return updated


def get_conversations(db: Session, user_id: int) -> List[schemas.Conversation]:
    """Get list of conversations (unique users the current user has messaged with)"""
    # Get all unique users the current user has communicated with
    sent_to = db.query(models.Message.receiver_id).filter(
        models.Message.sender_id == user_id
    ).distinct()
    
    received_from = db.query(models.Message.sender_id).filter(
        models.Message.receiver_id == user_id
    ).distinct()
    
    # Combine both sets
    all_users = set()
    for (uid,) in sent_to.all():
        all_users.add(uid)
    for (uid,) in received_from.all():
        all_users.add(uid)
    
    conversations = []
    for other_user_id in all_users:
        # Get the last message in the conversation
        last_message = db.query(models.Message).filter(
            or_(
                and_(models.Message.sender_id == user_id, models.Message.receiver_id == other_user_id),
                and_(models.Message.sender_id == other_user_id, models.Message.receiver_id == user_id)
            )
        ).order_by(models.Message.created_at.desc()).first()
        
        if not last_message:
            continue
        
        # Count unread messages
        unread_count = db.query(models.Message).filter(
            models.Message.sender_id == other_user_id,
            models.Message.receiver_id == user_id,
            models.Message.is_read == False
        ).count()
        
        conversations.append(schemas.Conversation(
            user_id=other_user_id,
            user_name=_get_user_full_name(db, other_user_id),
            last_message=last_message.content,
            last_message_time=last_message.created_at or datetime.utcnow(),
            unread_count=unread_count
        ))
    
    # Sort by last message time
    conversations.sort(key=lambda c: c.last_message_time, reverse=True)
    
    return conversations


def get_unread_count(db: Session, user_id: int) -> int:
    """Get total count of unread messages for a user"""
    return db.query(models.Message).filter(
        models.Message.receiver_id == user_id,
        models.Message.is_read == False
    ).count()


def get_available_users(db: Session, current_user_id: int) -> List[schemas.UserListItem]:
    """Get list of users available to message"""
    users = db.query(models.User).filter(
        models.User.user_id != current_user_id
    ).all()
    
    result = []
    for user in users:
        full_name = _get_user_full_name(db, user.user_id)
        result.append(schemas.UserListItem(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            full_name=full_name
        ))
    
    return result
