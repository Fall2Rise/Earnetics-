from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.permission_manager import permission_manager

router = APIRouter(prefix='/api/permissions', tags=['permissions'])


class PermissionPayload(BaseModel):
    scope: str
    granted: bool


@router.get('/{subject}')
def list_permissions(subject: str):
    permissions = permission_manager.list_permissions(subject)
    return {'permissions': [permission.__dict__ for permission in permissions]}


@router.post('/{subject}')
def set_permission(subject: str, payload: PermissionPayload):
    permission_manager.set_permission(subject, payload.scope, payload.granted)
    return {'status': 'updated'}


@router.delete('/{subject}')
def revoke_subject(subject: str):
    permission_manager.revoke_subject(subject)
    return {'status': 'revoked'}
