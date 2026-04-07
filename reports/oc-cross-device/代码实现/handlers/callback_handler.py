"""
回调处理模块
支持任务执行完成后的回调通知
"""

import logging
import time
import threading
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import queue

logger = logging.getLogger(__name__)


class CallbackStatus(Enum):
    """回调状态"""
    PENDING = "pending"
    SENT = "sent"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


@dataclass
class Callback:
    """回调定义"""
    callback_id: str
    url: str
    event: str
    payload: Dict[str, Any]
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 10
    retry_count: int = 3
    retry_delay: int = 5
    
    status: CallbackStatus = CallbackStatus.PENDING
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CallbackHandler:
    """回调处理器 - 管理所有回调的生命周期"""
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 1000):
        self.callbacks: Dict[str, Callback] = {}
        self.dispatch_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.workers: List[threading.Thread] = []
        self.max_workers = max_workers
        self.running = False
        self._callbacks: Dict[str, List[Callable]] = {}  # 事件回调
    
    def start(self):
        """启动回调处理工作线程"""
        if self.running:
            return
        self.running = True
        for i in range(self.max_workers):
            t = threading.Thread(target=self._worker, daemon=True, name=f"callback-worker-{i}")
            t.start()
            self.workers.append(t)
        logger.info(f"启动 {self.max_workers} 个回调处理线程")
    
    def stop(self):
        """停止回调处理"""
        self.running = False
        for t in self.workers:
            t.join(timeout=2)
        self.workers.clear()
        logger.info("回调处理线程已停止")
    
    def _worker(self):
        """工作线程"""
        while self.running:
            try:
                callback = self.dispatch_queue.get(timeout=1)
                self._execute_callback(callback)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"回调执行异常: {e}")
    
    def _execute_callback(self, callback: Callback):
        """执行回调请求"""
        callback.attempts += 1
        callback.status = CallbackStatus.RETRYING if callback.attempts > 1 else CallbackStatus.PENDING
        callback.sent_at = datetime.now()
        
        try:
            import requests
            response = requests.request(
                method=callback.method,
                url=callback.url,
                json=callback.payload,
                headers={"Content-Type": "application/json", **callback.headers},
                timeout=callback.timeout
            )
            callback.response = {
                "status_code": response.status_code,
                "body": response.text[:500]
            }
            
            if 200 <= response.status_code < 300:
                callback.status = CallbackStatus.SUCCESS
                callback.completed_at = datetime.now()
                logger.info(f"回调成功: {callback.callback_id}")
            else:
                callback.status = CallbackStatus.FAILED
                callback.error = f"HTTP {response.status_code}"
                self._maybe_retry(callback)
                
        except Exception as e:
            callback.status = CallbackStatus.FAILED
            callback.error = str(e)
            callback.response = {"error": str(e)}
            self._maybe_retry(callback)
    
    def _maybe_retry(self, callback: Callback):
        """决定是否重试"""
        if callback.attempts < callback.retry_count:
            callback.status = CallbackStatus.RETRYING
            retry_delay = callback.retry_delay * callback.attempts
            logger.warning(f"回调失败，将在 {retry_delay}s 后重试 ({callback.attempts}/{callback.retry_count}): {callback.callback_id}")
            time.sleep(retry_delay)
            self.dispatch_queue.put(callback)
        else:
            callback.status = CallbackStatus.FAILED
            callback.completed_at = datetime.now()
            logger.error(f"回调彻底失败: {callback.callback_id} - {callback.error}")
    
    def schedule(self, url: str, event: str, payload: Dict[str, Any],
                 method: str = "POST", headers: Dict[str, str] = None,
                 retry_count: int = 3, retry_delay: int = 5) -> Callback:
        """安排一个回调"""
        import uuid
        callback = Callback(
            callback_id=str(uuid.uuid4())[:12],
            url=url,
            event=event,
            payload=payload,
            method=method,
            headers=headers or {},
            retry_count=retry_count,
            retry_delay=retry_delay
        )
        self.callbacks[callback.callback_id] = callback
        
        try:
            self.dispatch_queue.put_nowait(callback)
            logger.info(f"回调已安排: {callback.callback_id} -> {url}")
        except queue.Full:
            logger.error("回调队列已满，拒绝回调")
            callback.status = CallbackStatus.FAILED
            callback.error = "Queue full"
        
        return callback
    
    def on(self, event: str, handler: Callable):
        """注册事件回调处理器"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(handler)
    
    def emit(self, event: str, data: Dict[str, Any]):
        """触发事件回调"""
        handlers = self._callbacks.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"事件处理器执行失败: {event} - {e}")
    
    def get_callback(self, callback_id: str) -> Optional[Callback]:
        return self.callbacks.get(callback_id)
    
    def list_callbacks(self, status: CallbackStatus = None, limit: int = 50) -> List[Callback]:
        callbacks = sorted(self.callbacks.values(), key=lambda c: c.created_at, reverse=True)
        if status:
            callbacks = [c for c in callbacks if c.status == status]
        return callbacks[:limit]
    
    def cleanup(self, older_than_hours: int = 24):
        """清理旧回调记录"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        to_remove = [
            cid for cid, c in self.callbacks.items()
            if c.completed_at and c.completed_at < cutoff
        ]
        for cid in to_remove:
            del self.callbacks[cid]
        return len(to_remove)
