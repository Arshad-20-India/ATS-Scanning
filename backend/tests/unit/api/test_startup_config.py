from __future__ import annotations

import dataclasses

import pytest
from unittest.mock import patch


def _replace_main_settings(**overrides):
    """
    Settings is a frozen dataclass -- can't patch.object() a field on
    the instance directly. Build a modified copy via
    dataclasses.replace() and patch the module-local `settings` name
    that app.api.main actually reads from (patching
    app.core.config.settings wouldn't affect main's already-bound
    `from ... import settings`).
    """
    from app.api import main as main_module

    return patch.object(main_module, "settings", dataclasses.replace(main_module.settings, **overrides))


def test_production_with_default_jwt_secret_fails_fast():
    from app.api.main import InsecureConfigurationError, create_app

    with _replace_main_settings(
        environment="production",
        jwt_secret_key="dev-only-insecure-secret-change-in-production",
    ):
        with pytest.raises(InsecureConfigurationError):
            create_app()


def test_production_with_real_jwt_secret_starts_normally():
    from app.api.main import create_app

    with _replace_main_settings(
        environment="production",
        jwt_secret_key="a-real-randomly-generated-secret-value",
    ):
        app = create_app()
        assert app is not None


def test_development_with_default_jwt_secret_only_warns_not_raises():
    from app.api.main import create_app

    with _replace_main_settings(
        environment="development",
        jwt_secret_key="dev-only-insecure-secret-change-in-production",
    ):
        app = create_app()  # must not raise
        assert app is not None
