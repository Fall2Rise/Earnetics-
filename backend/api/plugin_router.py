from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.plugin_registry import PluginEntry, plugin_registry

router = APIRouter(prefix='/api/plugins', tags=['plugins'])


class PluginPayload(BaseModel):
    name: str
    version: str
    description: str
    repository: str | None = None
    entrypoint: str | None = None


@router.get('')
def list_plugins():
    plugins = plugin_registry.list_plugins()
    return {'plugins': [plugin.__dict__ for plugin in plugins]}


@router.post('')
def register_plugin(payload: PluginPayload):
    try:
        plugin_registry.register_plugin(PluginEntry(**payload.dict()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {'status': 'registered'}


@router.post('/{name}/activate')
def activate_plugin(name: str):
    try:
        plugin = plugin_registry.activate_plugin(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {'status': 'activated', 'plugin': plugin.__dict__}


@router.post('/{name}/deactivate')
def deactivate_plugin(name: str):
    try:
        plugin = plugin_registry.deactivate_plugin(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {'status': 'deactivated', 'plugin': plugin.__dict__}
