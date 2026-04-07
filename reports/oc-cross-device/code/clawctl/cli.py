#!/usr/bin/env python3
"""
clawctl CLI - 命令行工具
用法示例：
  clawctl status                          # 查看状态
  clawctl trigger tech-analyst            # 触发任务
  clawctl send --channel dingtalk "测试"  # 发送消息
  clawctl exec "生成今日简报"             # 直接执行任务
"""

import sys
import json
import argparse
import logging

from core.client import OpenClawClient
from core.task import Task, TaskManager
from core.config import Config


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def cmd_status(client: OpenClawClient):
    resp = client.get_status()
    if resp.success:
        print("✅ OpenClaw 连接正常")
        print(json.dumps(resp.data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 连接失败: {resp.error}")


def cmd_trigger(client: OpenClawClient, task_manager: TaskManager, name: str):
    task = Task(name=name, action="spawn", params={"task": name})
    task_manager.submit(task)
    task_manager.execute_async(task)
    print(f"🚀 任务已提交: {task.id} | {name}")
    print(f"   使用 'clawctl task {task.id}' 查询状态")


def cmd_send(client: OpenClawClient, channel: str, message: str):
    resp = client.send_message(channel=channel, message=message)
    if resp.success:
        print(f"✅ 消息已发送到 {channel}")
    else:
        print(f"❌ 发送失败: {resp.error}")


def cmd_exec(client: OpenClawClient, task_manager: TaskManager, task_str: str):
    task = Task(name=f"cli:{task_str[:50]}", action="spawn", params={"task": task_str})
    task_manager.submit(task)
    print(f"🚀 正在执行: {task.id}")
    task_manager.execute_async(task)


def cmd_task(task_manager: TaskManager, task_id: str, format_: str = "json"):
    task = task_manager.get(task_id)
    if not task:
        print(f"❌ 任务不存在: {task_id}")
        return
    if format_ == "json":
        print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False))
    else:
        d = task.to_dict()
        print(f"任务ID:   {d['id']}")
        print(f"名称:     {d['name']}")
        print(f"状态:     {d['status']}")
        print(f"创建时间: {d['created_at']}")
        if d.get('duration_ms'):
            print(f"耗时:     {d['duration_ms']}ms")


def cmd_list(task_manager: TaskManager, status: str = None):
    from core.task import TaskStatus
    s = TaskStatus(status) if status else None
    tasks = task_manager.list(status=s)
    if not tasks:
        print("暂无任务")
        return
    for t in tasks:
        d = t.to_dict()
        emoji = {"pending": "⏳", "queued": "📋", "running": "🔄", "success": "✅", "failed": "❌"}.get(d["status"], "❓")
        print(f"{emoji} [{d['id']}] {d['name']} | {d['status']} | {d.get('duration_ms', '-')}ms")


def main():
    parser = argparse.ArgumentParser(prog="clawctl", description="OpenClaw 跨设备控制工具")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    sub = parser.add_subparsers(dest="cmd")

    # status
    sub.add_parser("status", help="查看系统状态")

    # trigger
    p_trigger = sub.add_parser("trigger", help="触发任务")
    p_trigger.add_argument("name", help="任务名称")

    # send
    p_send = sub.add_parser("send", help="发送消息")
    p_send.add_argument("--channel", "-c", default="dingtalk", help="渠道")
    p_send.add_argument("message", help="消息内容")

    # exec
    p_exec = sub.add_parser("exec", help="直接执行任务")
    p_exec.add_argument("task", help="任务描述")

    # task
    p_task = sub.add_parser("task", help="查看任务详情")
    p_task.add_argument("task_id")
    p_task.add_argument("--format", "-f", choices=["json", "text"], default="text")

    # list
    p_list = sub.add_parser("list", help="列出任务")
    p_list.add_argument("--status", "-s", help="状态过滤")

    args = parser.parse_args()

    setup_logging("DEBUG" if args.debug else "INFO")

    # 初始化客户端
    try:
        cfg = Config(args.config)
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)

    client = OpenClawClient(
        base_url=cfg.openclaw.get("base_url", "http://localhost:18789"),
        api_key=cfg.openclaw.get("api_key"),
        timeout=cfg.openclaw.get("timeout", 30),
    )
    task_manager = TaskManager(client)

    # 执行命令
    if args.cmd == "status":
        cmd_status(client)
    elif args.cmd == "trigger":
        cmd_trigger(client, task_manager, args.name)
    elif args.cmd == "send":
        cmd_send(client, args.channel, args.message)
    elif args.cmd == "exec":
        cmd_exec(client, task_manager, args.task)
    elif args.cmd == "task":
        cmd_task(task_manager, args.task_id, args.format)
    elif args.cmd == "list":
        cmd_list(task_manager, args.status)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
