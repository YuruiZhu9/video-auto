---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 54503f885376e33a7cd255e7889e3ce8
    PropagateID: 54503f885376e33a7cd255e7889e3ce8
    ReservedCode1: 3045022049341b0f7110798352c9f8e9c9aba4c7093a73ed46bd6296f50e27dad5d6080c022100e9342d4469f613a803a701ad64ffccabcffc9ab72a756e2a02acb04fa15660a0
    ReservedCode2: 304502201a896e447f8514220181331bb5d5a45bd4b2a0094db8943c4eb8f3abb965a934022100de291a4baf71b8ac29db90a29f5e983c53f8056d4e58e57a11a2f52efdf0329a
---

# Memory


## Recent Session Notes (2026-04-02 07:34)

>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...


## Recent Session Notes (2026-04-09 06:07)

TICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[assistant]: Now let me check the latest execution report and search for any genuinely new methods I haven't covered yet.
Now I have a clear picture of the knowledge base. It's already comprehensive (~117 docs), with the last execution (today 12:59 PM) adding B站弹幕解析 and bibigpt-skill. This execution (1:31 PM) should add genuinely new content. Let me focus on **视频解析 → PKM（个人知识库）同步** and **GitHub Actions 自动化 Pipeline**，两个真正有价值的空白领域。
Now let me update the index and create the execution report.
Now let me create...


## Recent Session Notes (2026-04-09 07:10)

>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...

## ⚠️ 文件删除原则（2026-04-09 教训）

**不要随意删除用户积累的内容文件。**

教训：语音克隆方案报告.md 是用户长期维护的技术文档，删除后才发现 model-library-tts.md 内容覆盖不全，两者各有价值（云服务对比 vs 开源模型技术细节）。

**正确做法：**
- 合并前先读两个文件，确认内容覆盖关系
- 不确定时保留两个文件，由用户决定
- 涉及"整合/合并"操作：先读文件，再告知合并方案，得到确认后再执行

**可以安全删除的：**
- 明显是一次性脚本（无引用）
- 残留的 .bak / .pyc
- 空目录
- 已失效的 cron 任务引用路径

