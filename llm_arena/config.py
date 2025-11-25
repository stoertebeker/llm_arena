from __future__ import annotations
import os, tomllib
from pydantic import ValidationError
from .types import Config

def _resolve_env(value: str) -> str:
    if isinstance(value, str) and value.startswith("ENV:"):
        env_name = value.split("ENV:",1)[1]
        return os.environ.get(env_name, "")
    return value

def load_config(path: str = "config.toml") -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    # resolve ENV: for top-level providers and any judge/candidate with base_url/api_key
    if "providers" in raw:
        for k in ("base_url","api_key"):
            if k in raw["providers"]:
                raw["providers"][k] = _resolve_env(raw["providers"][k])
    for section in ("candidates","judges"):
        if section in raw:
            for entry in raw[section]:
                for k in ("base_url","api_key"):
                    if k in entry:
                        entry[k] = _resolve_env(entry[k])
    try:
        return Config.model_validate(raw)
    except ValidationError as e:
        raise SystemExit(f"Config validation error:\n{e}") from e
