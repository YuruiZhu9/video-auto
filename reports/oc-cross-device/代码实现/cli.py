"""命令行工具 — clawremote"""

import sys
import argparse
import asyncio
from core.client import OpenClawClient
from core.auth import AuthManager, KeyLevel


async def cmd_status(args):
    client = OpenClawClient()
    status = await client.get_status()
    print("OpenClaw Gateway 状态：")
    print(f"  可达：{status.get('reachable', 'unknown')}")
    agents = status.get("agents", [])
    print(f"  活跃 Agent：{len(agents)}")
    for a in agents:
        print(f"    - {a.get('name')}: {a.get('status')}")
    await client.close()


async def cmd_send(args):
    client = OpenClawClient()
    result = await client.send_message(
        channel=args.channel,
        message=args.message,
        target=args.target,
    )
    print(f"消息已发送：{result}")
    await client.close()


async def cmd_exec(args):
    client = OpenClawClient()
    result = await client.spawn_agent(
        task=args.task,
        agent=args.agent,
        timeout_seconds=args.timeout,
    )
    print(f"任务已触发：{result.get('session_key')}")
    await client.close()


async def cmd_key_create(args):
    auth = AuthManager()
    level = KeyLevel.from_str(args.level)
    raw_key, api_key = auth.create_key(level, args.name)
    print(f"✅ API Key 已生成（只显示一次，请妥善保管）：")
    print(f"   {raw_key}")
    print(f"   名称：{api_key.name}")
    print(f"   权限：{api_key.level.name}")
    print(f"   标识：{api_key.display_key}")


async def cmd_key_list(args):
    auth = AuthManager()
    keys = auth.list_keys()
    print(f"共 {len(keys)} 个 Key：")
    for k in keys:
        status = "✅" if k["enabled"] else "❌"
        exp = f" | 过期：{k['expires_at']}" if k["expires_at"] else ""
        print(f"  {status} {k['display_key']} | {k['level']} | {k['name']}{exp}")


async def cmd_key_revoke(args):
    auth = AuthManager()
    ok = auth.revoke_key(args.key_id)
    print(f"Key 已吊销" if ok else f"Key 未找到")


def main():
    parser = argparse.ArgumentParser(description="ClawRemote CLI")
    sub = parser.add_subparsers()

    p_status = sub.add_parser("status", help="查看 OpenClaw 状态")
    p_status.set_defaults(func=cmd_status)

    p_send = sub.add_parser("send", help="发送消息")
    p_send.add_argument("--channel", "-c", default="dingtalk", help="渠道")
    p_send.add_argument("--target", "-t", help="目标 ID")
    p_send.add_argument("message", help="消息内容")
    p_send.set_defaults(func=cmd_send)

    p_exec = sub.add_parser("exec", help="执行任务")
    p_exec.add_argument("task", help="任务描述")
    p_exec.add_argument("--agent", help="Agent 名称")
    p_exec.add_argument("--timeout", "-T", type=int, default=300)
    p_exec.set_defaults(func=cmd_exec)

    p_key = sub.add_parser("key", help="Key 管理")
    p_key_sub = p_key.add_subparsers()
    k_create = p_key_sub.add_parser("create", help="创建 Key")
    k_create.add_argument("name", help="Key 名称")
    k_create.add_argument("--level", "-l", default="EXECUTE", choices=["READ_ONLY", "EXECUTE", "ADMIN"])
    k_create.set_defaults(func=cmd_key_create)
    k_list = p_key_sub.add_parser("list", help="列出 Key")
    k_list.set_defaults(func=cmd_key_list)
    k_revoke = p_key_sub.add_parser("revoke", help="吊销 Key")
    k_revoke.add_argument("key_id", help="Key ID")
    k_revoke.set_defaults(func=cmd_key_revoke)

    args = parser.parse_args()
    if hasattr(args, "func"):
        asyncio.run(args.func(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
