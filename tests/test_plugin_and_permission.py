from __future__ import annotations

from pathlib import Path

from backend.permission_manager import PermissionManager
from backend.plugin_registry import PluginEntry, PluginRegistry


def test_plugin_registry_persistence_and_activation(tmp_path):
    store_path = tmp_path / "plugin_registry.json"
    registry = PluginRegistry(store=store_path)

    entry = PluginEntry(
        name="automation_suite",
        version="1.0.0",
        description="Automates marketing campaigns",
        repository="https://example.com/automation",
        entrypoint="automation.run",
    )

    registry.register_plugin(entry)
    plugins = registry.list_plugins()
    assert len(plugins) == 1
    assert plugins[0].active is False

    registry.activate_plugin("automation_suite")
    active_plugin = registry.list_plugins()[0]
    assert active_plugin.active is True

    registry.deactivate_plugin("automation_suite")
    inactive_plugin = registry.list_plugins()[0]
    assert inactive_plugin.active is False

    reloaded = PluginRegistry(store=store_path)
    persisted = reloaded.list_plugins()[0]
    assert persisted.name == "automation_suite"
    assert persisted.description == "Automates marketing campaigns"
    assert persisted.active is False


def test_permission_manager_set_toggle_and_revoke(tmp_path):
    store_path = tmp_path / "permission_store.json"
    manager = PermissionManager(store=store_path)

    manager.set_permission("marketing_agent", "workflows:run", True)
    permissions = manager.list_permissions("marketing_agent")
    assert len(permissions) == 1
    assert permissions[0].scope == "workflows:run"
    assert permissions[0].granted is True

    manager.set_permission("marketing_agent", "workflows:run", False)
    updated = manager.list_permissions("marketing_agent")[0]
    assert updated.granted is False

    manager.set_permission("marketing_agent", "reports:view", True)
    assert len(manager.list_permissions("marketing_agent")) == 2

    manager.revoke_subject("marketing_agent")
    assert manager.list_permissions("marketing_agent") == []

    assert store_path.exists()
    reloaded = PermissionManager(store=store_path)
    assert reloaded.list_permissions("marketing_agent") == []
