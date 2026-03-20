"""Configuration helpers for provider runtime selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProviderRuntimeConfig:
    """Resolved provider-runtime configuration."""

    backend: str
    data_dir: Path | None = None


def resolve_provider_runtime_config(
    backend: str | None = None,
    data_dir: str | Path | None = None,
) -> ProviderRuntimeConfig:
    """Resolve provider settings from CLI arguments or environment variables."""

    resolved_backend = (backend or os.getenv("EFA_PROVIDER_BACKEND") or "live").strip().lower()
    resolved_data_dir = data_dir or os.getenv("EFA_PROVIDER_DATA_DIR")
    return ProviderRuntimeConfig(
        backend=resolved_backend,
        data_dir=Path(resolved_data_dir).expanduser().resolve() if resolved_data_dir else None,
    )
