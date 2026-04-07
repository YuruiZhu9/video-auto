#!/usr/bin/env python3
"""配置管理模块"""

import os
import yaml
from typing import Any, Optional


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def expand_env(val: Any) -> Any:
    """递归替换 ${VAR} 形式的环境变量"""
    if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
        var = val[2:-1]
        return os.environ.get(var, "")
    if isinstance(val, dict):
        return {k: expand_env(v) for k, v in val.items()}
    if isinstance(val, list):
        return [expand_env(i) for i in val]
    return val


class Config:
    def __init__(self, path: str = "config.yaml"):
        self._raw = load_yaml(path)
        self._raw = expand_env(self._raw)
        self.server = self._raw.get("server", {})
        self.openclaw = self._raw.get("openclaw", {})
        self.auth = self._raw.get("auth", {})
        self.webhook = self._raw.get("webhook", {})
        self.notify = self._raw.get("notify", {})
        self.logging_cfg = self._raw.get("logging", {})

    def get(self, *keys, default=None) -> Any:
        d = self._raw
        for k in keys:
            if isinstance(d, dict):
                d = d.get(k, default)
            else:
                return default
        return d
