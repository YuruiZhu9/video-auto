"""Webhook Handler - 独立的 Webhook 接收处理"""
import logging
from typing import Any, Dict

from ..core.trigger import WebhookTrigger

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Webhook 接收处理器"""

    def __init__(self, trigger_registry: list):
        self.triggers: list = trigger_registry

    def register_trigger(self, trigger: WebhookTrigger):
        self.triggers.append(trigger)

    def handle(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Dict[str, Any],
        client_ip: str = "unknown",
    ) -> Dict[str, Any]:
        """处理到来的 Webhook 请求"""
        for trigger in self.triggers:
            if trigger.matches(path, method):
                if not trigger.verify(headers, body):
                    logger.warning(f"Webhook verification failed for {path}")
                    return {"matched": True, "verified": False, "error": "Verification failed"}

                trigger.mark_triggered()
                logger.info(f"Webhook triggered: {trigger.task_id}")
                return {
                    "matched": True,
                    "verified": True,
                    "task_id": trigger.task_id,
                    "trigger_count": trigger.trigger_count,
                }

        return {"matched": False, "error": "No matching trigger"}
