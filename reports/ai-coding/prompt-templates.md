# AI 编程 Prompt 模板库

> 持续更新，积累有效 Prompt 模式

---

## 📌 基础框架

所有 Prompt 的基础结构：

```
Role（角色）   → AI 的身份设定
Goal（目标）   → 明确的交付物
Constraints（约束） → 编码规范和限制条件
```

---

## 1️⃣ 代码解释

**中文版：**
```
请逐行解释这段代码，重点说明：
1. 每个函数的作用（一句话描述）
2. 数据流向（输入 → 处理 → 输出）
3. 关键的算法逻辑
4. 你认为值得注意的潜在问题

代码：
[粘贴代码]
```

**English Version:**
```
Explain this code line by line, focusing on:
1. What each function does (one-sentence summary)
2. The data flow (input → processing → output)
3. The key algorithm/logic
4. Any potential issues worth noting

Code:
[paste code]
```

---

## 2️⃣ 代码审查

**标准版：**
```
请审查以下代码，重点关注：
1. 逻辑错误 — 算法是否符合预期
2. 边界条件 — null、空数组、异常输入如何处理
3. 性能问题 — N+1查询、内存泄漏风险
4. 安全漏洞 — 注入、硬编码密钥、XSS等
5. 代码风格 — 是否符合最佳实践

代码：
[粘贴代码]
```

**安全专项版：**
```
Act as a senior security engineer. Review this code for:
1. SQL injection and XSS vulnerabilities
2. Authentication/authorization bypasses
3. Insecure deserialization risks
4. Hardcoded secrets or credentials
5. Dependency authenticity (check if packages actually exist)

Code:
[paste code]
```

---

## 3️⃣ 优化建议

```
分析这段代码的性能瓶颈，给出：
1. 当前复杂度分析（时间 + 空间）
2. 主要性能瓶颈定位
3. 2-3 个优化方案（保守 → 激进）
4. 每个方案的权衡取舍

代码：
[粘贴代码]
```

---

## 4️⃣ 遵循已有模式

```
Following the same pattern as [existing_function_name] above,
implement a function to [specific_task].

Constraints:
- Same error handling approach
- Same naming conventions  
- Same type hints and docstrings style
- Include appropriate tests
```

---

## 5️⃣ 约束声明（防止 AI 幻觉）

```
Write a [language] function that [task] with these constraints:
- Must handle [specific edge case]
- Must validate input before processing
- Must include error handling for [specific errors]
- Should not use [specific antipatterns]
- Must output [specific format]

Example input: [input example]
Expected output: [output example]
```

---

## 6️⃣ 分步重构

```
我需要重构这段代码，请分步指导：

当前状态：[描述现状]
目标状态：[描述目标]

请：
1. 先解释当前代码的工作原理
2. 给出 3-5 步重构计划
3. 每步实现前说明原因
4. 最后验证是否符合预期

代码：
[粘贴代码]
```

---

## 7️⃣ 测试用例生成

```
Generate unit tests for this function that cover:
1. Happy path (valid inputs)
2. Error cases (invalid inputs)
3. Edge cases (empty, zero, very large values)
4. Each test with a descriptive name

Use [test framework, e.g., pytest/Jest/JUnit]

Function:
[paste code]
```

---

## 8️⃣ 调试求助

```
This code is throwing an error:
"Error: [paste error message]"

Here's the full stack trace:
[paste stack trace]

Here's sample data causing the error:
[paste data]

Before suggesting a fix, please:
1. Explain why the error is occurring
2. Identify the root cause
3. Then propose the fix with explanation
```

---

## 9️⃣ 架构设计讨论

```
I'm designing a [system feature] with these requirements:
1. [requirement 1]
2. [requirement 2]
3. [requirement 3]

Constraints:
- Technology: [tech stack]
- Scale: [expected load]
- Team: [team size / experience level]

Please:
1. Propose 2-3 architecture options with tradeoffs
2. Recommend the best option with reasoning
3. Identify potential risks
```

---

## 🔄 迭代精化模式

```
Step 1（初版）:
"Create a React hook that manages API pagination."

Step 2（加错误处理）:
"Great start. Now add error handling and a loading state to the hook."

Step 3（加高级功能）:
"Add support for changing page size and sorting parameters."

Step 4（加测试）:
"Now generate unit tests covering happy path, error cases, and edge cases."
```

---

*模板库由 AI Coding 助手 维护 | 更新于 2026-04-13*
