#!/usr/bin/env python3
"""
clawctl Server - Web 服务入口
启动 HTTP API 服务，提供跨设备控制能力
"""

import os
import sys
import json
import logging
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.client import OpenClawClient
from core.task import TaskManager, TaskStatus
from core.auth import AuthManager, APIKey, KeyLevel
from core.config import Config
from core.scheduler import Scheduler
from core.template_loader import TemplateLoader
from core.database import TaskDatabase, TaskRecord
from core.task_dag import get_dag_manager
from handlers.http_handler import create_app
from handlers.sse_handler import SseManager, EventType
from handlers.dag_routes import dag_bp, init_dag_routes
from notify import NotifyManager, DingTalkNotifier


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def build_app(cfg: Config):
    """构建完整应用"""
    # ── 核心组件 ────────────────────────────────────────────────
    client = OpenClawClient(
        base_url=cfg.openclaw.get("base_url", "http://localhost:18789"),
        api_key=cfg.openclaw.get("api_key") or os.environ.get("OPENCLAW_API_KEY", ""),
        timeout=cfg.openclaw.get("timeout", 30),
    )
    task_manager = TaskManager(client)

    # ── 持久化数据库（SQLite）────────────────────────────────────
    db = TaskDatabase(os.environ.get("CLAWCTL_DB_PATH", "/workspace/reports/oc-cross-device/data/tasks.db"))

    # ── SSE 实时推送管理器 ───────────────────────────────────────
    sse_manager = SseManager(heartbeat_interval=25)

    # ── 流式执行管理器 (v2.2.0) ─────────────────────────────────
    try:
        from core.stream_manager import init_stream_manager
        stream_mgr = init_stream_manager(max_streams=50, max_history=30)
        logger.info("🌊 StreamManager 已初始化 (v2.2.0 流式执行)")
    except ImportError:
        stream_mgr = None
        logger.warning("⚠️ StreamManager 未找到，流式执行功能不可用")

    # ── 通知管理器 ────────────────────────────────────────────
    notify_mgr = NotifyManager()
    dingtalk_token = cfg.webhook.get("dingtalk", {}).get("token") or os.environ.get("DINGTALK_TOKEN", "")
    dingtalk_secret = cfg.webhook.get("dingtalk", {}).get("secret") or os.environ.get("DINGTALK_SECRET", "")
    if dingtalk_token:
        notifier = DingTalkNotifier(token=dingtalk_token, secret=dingtalk_secret)
        notify_mgr.register("dingtalk", notifier)

    # 任务完成回调 → 持久化 + 通知 + SSE推送
    def on_task_done(task):
        # 1. 持久化到 SQLite
        record = TaskRecord(
            id=task.id,
            name=task.name,
            action=task.action,
            params=json.dumps(task.params, ensure_ascii=False),
            status=task.status.value,
            priority=task.priority.name,
            notify=task.notify,
            notify_channel=task.notify_channel,
            result=json.dumps(task.result, ensure_ascii=False) if task.result else None,
            error=task.error,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            duration_ms=task.duration_ms(),
        )
        db.save_task(record)

        # 2. SSE 实时推送（通知所有在线客户端）
        task_dict = task.to_dict()
        sse_manager.emit_task_update(task_dict, broadcast=True)

        # 3. 钉钉/邮件通知
        if not task.notify:
            return
        if task.status == TaskStatus.SUCCESS:
            notify_mgr.send_task_complete(
                task.name,
                task.duration_ms() or 0,
                str(task.result)[:200] if task.result else "完成",
                channel=task.notify_channel,
            )
        elif task.status == TaskStatus.FAILED:
            notify_mgr.send_alert(
                "任务失败",
                f"{task.name} 失败: {task.error}",
                channel=task.notify_channel,
            )
    task_manager.on_done(on_task_done)

    # ── 模板加载器 ─────────────────────────────────────────────
    tpl_path = os.environ.get("CLAWCTL_TEMPLATES", "clawctl/templates/schedules.yaml")
    template_loader = TemplateLoader(yaml_path=tpl_path, hot_reload=True)
    task_manager.templates = template_loader.list()

    # ── 定时任务调度器 ─────────────────────────────────────────
    scheduler = Scheduler(task_manager, notify_mgr, client)
    # 从 YAML 加载定时任务
    if os.path.exists(tpl_path):
        scheduler.load_from_yaml(tpl_path)
    scheduler.start()

    # ── 认证管理器 ─────────────────────────────────────────────
    auth_mgr = AuthManager()
    for k in cfg.auth.get("keys", []):
        level_map = {"read": KeyLevel.READ, "exec": KeyLevel.EXEC, "admin": KeyLevel.ADMIN}
        auth_mgr.add_key(APIKey(
            id=k["id"],
            key=k["key"],
            level=level_map.get(k["level"], KeyLevel.READ),
            name=k.get("name", ""),
            ip_whitelist=k.get("ip_whitelist"),
            rate_limit=k.get("rate_limit", 60),
        ))

    webhook_secret = cfg.webhook.get("secret") or os.environ.get("WEBHOOK_SECRET", "")
    if webhook_secret:
        auth_mgr.set_webhook_secret(webhook_secret)

    # ── 钉钉快捷命令处理器 ───────────────────────────────────────
    if dingtalk_token:
        try:
            from handlers.dingtalk_handler import DingTalkNotifier, CommandRouter
            dt_notifier = DingTalkNotifier(token=dingtalk_token, secret=dingtalk_secret)
            dt_notifier.router = CommandRouter()
            logger.info("📱 钉钉交互处理器已初始化（支持快捷命令）")
        except ImportError as e:
            logger.warning(f"⚠️ 钉钉处理器导入失败: {e}")

    # ── Telegram Bot ───────────────────────────────────────────
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    bot = None
    if telegram_token:
        try:
            from handlers.telegram_bot import TelegramBot
            bot = TelegramBot(
                token=telegram_token,
                chat_id=telegram_chat_id,
                notify_mgr=notify_mgr,
                task_manager=task_manager,
                client=client,
            )
            bot.start_polling()
            logger = logging.getLogger("clawctl.server")
            logger.info("🤖 Telegram Bot 已启动 (Polling 模式)")
        except ImportError:
            logger.warning("Telegram Bot 依赖未安装 (pip install python-telegram-bot)")

    # 创建 Flask App（含数据库 + SSE）
    app = create_app(client, task_manager, auth_mgr, scheduler, template_loader, db, sse_manager)

    # ── DAG 任务编排路由 ─────────────────────────────────────────
    dag_mgr = get_dag_manager()
    init_dag_routes(task_manager, client, auth_mgr, notify_mgr, sse_manager,
                    dag_mgr, template_loader)
    app.register_blueprint(dag_bp)
    logger.info("🔀 DAG 任务编排路由已注册 (/api/v1/dag/)")

    # 注册 clawctl:// URL Scheme 路由
    try:
        from handlers.url_scheme import register_url_scheme_routes
        register_url_scheme_routes(app, task_manager, client, auth_mgr, notify_mgr, sse_manager)
        logger.info("🔗 clawctl:// URL Scheme 路由已注册")
    except ImportError:
        logger.warning("⚠️ url_scheme.py 未找到，跳过 URL Scheme 注册")

    # 注册 SSE 路由
    try:
        from handlers.sse_handler import register_sse_routes
        register_sse_routes(app, sse_manager)
        logger.info("📡 SSE 实时推送路由已注册")
    except Exception:
        logger.warning("⚠️ SSE 路由注册失败")

    # ── 流式执行路由 (v2.2.0) ────────────────────────────────────
    if stream_mgr:
        try:
            from handlers.stream_routes import _build_stream_blueprint
            stream_bp = _build_stream_blueprint(
                client=client,
                task_manager=task_manager,
                auth_manager=auth_mgr,
                db=db,
                notify_mgr=notify_mgr,
                stream_mgr=stream_mgr,
            )
            app.register_blueprint(stream_bp)
            logger.info("🌊 流式执行路由已注册 (/api/v1/stream/*)")
        except ImportError as e:
            logger.warning(f"⚠️ 流式路由注册失败: {e}")

    # ── 多实例管理器 (v2.4.0) ───────────────────────────────────
    try:
        from core.multi_instance import init_multi_instance_manager, get_multi_instance_manager
        from core.monitor import init_monitoring, get_monitoring_manager

        mi_mgr = init_multi_instance_manager()

        # 从配置加载预注册实例
        for inst_cfg in cfg.multi_instance.get("instances", []):
            from core.multi_instance import InstanceInfo
            import os as _os
            inst = InstanceInfo(
                id=inst_cfg["id"],
                name=inst_cfg["name"],
                base_url=inst_cfg["base_url"],
                api_key=inst_cfg.get("api_key") or _os.environ.get(f"OPENCLAW_API_KEY_{inst_cfg['id'].upper()}", ""),
                group=inst_cfg.get("group", "default"),
                tags=inst_cfg.get("tags", []),
                max_concurrent=inst_cfg.get("max_concurrent", 5),
            )
            mi_mgr.register_instance(inst)
            logger.info(f"  🏢 已注册实例: {inst.name} ({inst.base_url})")

        # 告警回调：钉钉推送
        def _alert_callback(alert, rule):
            severity_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}[alert.severity]
            msg = f"{severity_emoji} [{alert.severity.upper()}] {alert.rule_name}\n"
            msg += f"指标：{alert.metric} = {alert.current_value:.2f}，条件 {alert.condition} {alert.threshold}\n"
            msg += f"时间：{alert.fired_at.strftime('%Y-%m-%d %H:%M:%S')}"
            notify_mgr.send_alert(alert.rule_name, msg, channel="dingtalk")
            logger.warning(f"[ALERT] {alert.severity} - {alert.rule_name}: {alert.current_value:.2f}")

        # 健康检查回调：实例故障/恢复通知
        def _on_unhealthy(instance_id, error):
            info = mi_mgr.get_instance(instance_id)
            name = info.name if info else instance_id
            notify_mgr.send_alert(
                "实例故障",
                f"⚠️ OpenClaw 实例 **{name}** 健康检查失败\n错误：{error}\n实例已被熔断器摘除",
                channel="dingtalk",
            )

        def _on_recovered(instance_id):
            info = mi_mgr.get_instance(instance_id)
            name = info.name if info else instance_id
            notify_mgr.send_task_complete(
                "实例恢复",
                0,
                f"OpenClaw 实例 **{name}** 已恢复健康，重新接收任务",
                channel="dingtalk",
            )

        mi_mgr.set_health_callbacks(_on_unhealthy, _on_recovered)
        mi_mgr.start_health_check(interval=cfg.multi_instance.get("health_check_interval", 15))
        logger.info(f"🏢 多实例管理器已初始化 ({len(mi_mgr._instances)} 个实例)")

        # ── 监控系统 (v2.4.0) ──────────────────────────────────
        mon = init_monitoring(retention_minutes=cfg.monitoring.get("retention_minutes", 60))
        mon.start_collection(interval=cfg.monitoring.get("collection_interval", 5))

        # 注册告警规则
        for rule_cfg in cfg.monitoring.get("alert_rules", []):
            from core.monitor import AlertRule
            rule = AlertRule(
                id=rule_cfg["id"],
                name=rule_cfg["name"],
                metric=rule_cfg["metric"],
                condition=rule_cfg["condition"],
                threshold=float(rule_cfg["threshold"]),
                severity=rule_cfg.get("severity", "warning"),
                cooldown=int(rule_cfg.get("cooldown", 300)),
                channels=rule_cfg.get("channels", []),
            )
            mon.add_rule(rule)

        mon.set_alert_callback(_alert_callback)

        # OpenClaw 指标注入（定期更新实例统计）
        def _inject_openclaw_metrics():
            instances = mi_mgr.list_instances()
            active = sum(i.get("active_tasks", 0) for i in instances)
            total_req = sum(i.get("total_requests", 0) for i in instances)
            failed_req = sum(i.get("failed_requests", 0) for i in instances)
            avg_rt = sum(i.get("avg_response_time", 0) for i in instances) / max(len(instances), 1)
            healthy = sum(1 for i in instances if i.get("status") == "healthy")
            mon.update_openclaw_metrics(
                active_tasks=active,
                total_requests=total_req,
                failed_requests=failed_req,
                avg_response_ms=avg_rt,
                instances_healthy=healthy,
                instances_total=len(instances),
            )

        # 每 15 秒注入一次
        _inject_openclaw_metrics()
        threading.Thread(target=lambda: (
            _inject_openclaw_metrics() or
            [__import__('time').sleep(15) or _inject_openclaw_metrics() for _ in iter(int, 1)]
        ), daemon=True).start()
        logger.info(f"📊 监控系统已初始化 ({len(mon.list_rules())} 条告警规则)")

        # ── 监控路由注册 ──────────────────────────────────────
        try:
            from handlers.monitor_routes import monitor_bp
            app.register_blueprint(monitor_bp)
            logger.info("📡 监控 API 路由已注册 (/api/v1/monitor/*)")
        except ImportError as e:
            logger.warning(f"⚠️ 监控路由注册失败: {e}")

    except ImportError as e:
        logger.warning(f"⚠️ v2.4.0 模块导入失败: {e}")
        mi_mgr = None
        mon = None

    # Web Admin 静态文件路由（含 v3 PWA 版）
    web_admin_dir = os.path.join(os.path.dirname(__file__), "web_admin")
    if os.path.isdir(web_admin_dir):
        from flask import send_from_directory
        @app.route("/admin/")
        def admin_index():
            # 优先 v3
            v3_index = os.path.join(web_admin_dir, "v3", "index.html")
            return send_from_directory(web_admin_dir, "v3/index.html" if os.path.exists(v3_index) else ("index_v2.html" if os.path.exists(os.path.join(web_admin_dir, "index_v2.html")) else "index.html"))
        @app.route("/admin/<path:filename>")
        def admin_static(filename):
            # 优先 v3 子目录
            v3_path = os.path.join(web_admin_dir, "v3", filename)
            if os.path.exists(v3_path):
                return send_from_directory(os.path.join(web_admin_dir, "v3"), filename)
            return send_from_directory(web_admin_dir, filename)
        @app.route("/admin/v3/")
        def admin_v3_index():
            return send_from_directory(os.path.join(web_admin_dir, "v3"), "index.html")
        logger.info("🖥 Web Admin 路由已注册 (/admin/) — 含 v3 PWA 版")

    return app, client, task_manager, auth_mgr, notify_mgr, scheduler, bot, dag_mgr, stream_mgr


def main():
    cfg_path = os.environ.get("CLAWCTL_CONFIG", "config.yaml")
    try:
        cfg = Config(cfg_path)
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)

    setup_logging(cfg.logging_cfg.get("level", "INFO"))
    logger = logging.getLogger("clawctl.server")

    result = build_app(cfg)
    if len(result) == 8:
        app, client, task_manager, auth_mgr, notify_mgr, scheduler, bot, dag_mgr = result
        stream_mgr = None
    else:
        app, client, task_manager, auth_mgr, notify_mgr, scheduler, bot, dag_mgr, stream_mgr = result

    # 健康检查
    health = client.check_health()
    if not health:
        logger.warning("⚠️  OpenClaw Gateway 连接失败，服务启动但功能受限")

    host = cfg.server.get("host", "0.0.0.0")
    port = cfg.server.get("port", 8080)
    debug = cfg.server.get("debug", False)

    logger.info(f"🚀 clawctl 启动中...")
    logger.info(f"   HTTP API:  http://{host}:{port}")
    logger.info(f"   OpenClaw: {cfg.openclaw.get('base_url')}")
    logger.info(f"   调度任务:  {len(scheduler.list_jobs())} 个")
    logger.info(f"   快捷触发:  /api/v1/trigger/<name>")
    logger.info(f"   定时任务:  /api/v1/schedules")
    logger.info(f"   Webhook:   POST /api/v1/webhook")
    if bot:
        logger.info(f"   Telegram:  Polling 已启动")

    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    finally:
        scheduler.shutdown()
        if bot:
            bot.stop_polling()


if __name__ == "__main__":
    main()
