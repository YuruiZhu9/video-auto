"""配置文件加载"""

import os
import yaml
from typing import Optional


DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": False,
    },
    "openclaw": {
        "gateway_url": os.environ.get("OPENCLAW_GATEWAY_URL", "http://localhost:18789"),
        "api_key": os.environ.get("OPENCLAW_API_KEY", ""),
    },
    "auth": {
        "api_keys": [],
        "ip_whitelist": [],
        "rate_limit": {
            "READ_ONLY": 30,
            "EXECUTE": 20,
            "ADMIN": 60,
        },
    },
    "notify": {
        "dingtalk": {
            "enabled": True,
            "webhook_url": os.environ.get("DINGTALK_WEBHOOK_URL", ""),
            "secret": os.environ.get("DINGTALK_SECRET", ""),
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": "",
        },
    },
    "triggers": {
        "http": {"enabled": True},
        "webhook": {
            "enabled": True,
            "secret": os.environ.get("WEBHOOK_SECRET", ""),
        },
        "cron": {
            "enabled": False,
            "schedules": [],
        },
    },
    "templates": {
        "daily_brief": {
            "display_name": "每日简报",
            "description": "生成当日 AI 领域简报",
            "action": "spawn",
            "agent": "tech-analyst",
            "params": {"scope": "all"},
            "notify_on_complete": True,
        },
        "quick_scan": {
            "display_name": "快速扫描",
            "description": "执行快速信息抓取",
            "action": "spawn",
            "agent": "info-fetcher",
            "params": {"full": False},
            "notify_on_complete": True,
        },
        "business_check": {
            "display_name": "商业洞察",
            "description": "分析商业需求动态",
            "action": "spawn",
            "agent": "business-analyst",
            "params": {},
            "notify_on_complete": True,
        },
    },
}


def load_config(path: Optional[str] = None) -> dict:
    """加载配置文件，合并默认配置"""
    config = DEFAULT_CONFIG.copy()
    if path and os.path.exists(path):
        with open(path) as f:
            user_config = yaml.safe_load(f)
        deep_merge(config, user_config)
    # 环境变量覆盖
    for key in ["openclaw.gateway_url", "openclaw.api_key",
                "notify.dingtalk.webhook_url", "notify.dingtalk.secret"]:
        env_key = key.upper().replace(".", "_").replace("-", "_")
        if os.environ.get(env_key):
            keys = key.split(".")
            d = config
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = os.environ[env_key]
    return config


def deep_merge(base: dict, override: dict):
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
