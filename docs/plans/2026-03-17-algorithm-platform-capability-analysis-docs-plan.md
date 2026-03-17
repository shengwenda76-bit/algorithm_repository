# 算法平台功能分析文档 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 `数据计算与分析.mhtml` 生成一份中文、面向研发/架构的算法平台功能分析文档，并保留设计与交付过程记录。

**Architecture:** 先从 `mhtml` 中提取正文与内嵌图示信息，再将内容按算法平台能力域重组为研发可读的功能分析文档。交付物分为设计记录、功能分析正文和过程性计划三部分，保证来源清晰、边界明确、结论可追溯。

**Tech Stack:** Markdown, Git, PowerShell, Python 文本提取, MHTML/HTML 解析.

---

### Task 1: 提取原始材料关键信息

**Files:**
- Reference: `d:\02_dicitionary\github\h4\资料\数据计算与分析.mhtml`
- Create: `docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md`

**Step 1: 建立信息提取清单**

```text
- 是否识别出双运行态部署
- 是否识别出统一计算引擎
- 是否识别出统一 DAG 编排
- 是否识别出统一 Python 算子
- 是否识别出 NanoMQ 消息可靠性设计
```

**Step 2: 运行提取命令验证材料可读**

Run: `Select-String -Path 'd:\02_dicitionary\github\h4\资料\数据计算与分析.mhtml' -Pattern '架构|统一|NanoMQ|Flink|eKuiper|DAG|算子'`
Expected: 输出至少包含正文中的关键能力词和消息中间件选型信息

**Step 3: 提取内嵌图中的补充信息**

```text
- 统一 DAG 编排图
- 统一 Python 算子适配图
- 边缘单机消息流转图
- 集群消息流转图
```

**Step 4: 将提取结果整理为设计输入**

Run: `git show --stat --name-only 7c740d6 d23175a`
Expected: 可看到历史平台设计与初始化计划的文档线索，用于辅助理解而非替代原文

**Step 5: Commit**

```bash
git add docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md
git commit -m "docs: add capability analysis design record"
```

### Task 2: 写入设计记录文档

**Files:**
- Create: `docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md`

**Step 1: 固化已确认的设计结论**

```text
- 文档面向研发/架构
- 采用平台能力映射型结构
- 显式区分原文明确与平台化归纳
```

**Step 2: 校对设计边界**

Run: `rg "平台能力映射型|原文明确|平台化归纳|待澄清" docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md`
Expected: 设计文档中包含方法、边界和解释规则

**Step 3: 补全交付物说明**

```text
- 设计记录
- 过程计划
- 功能分析正文
```

**Step 4: 复核结构完整性**

Run: `rg "^## " docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md`
Expected: 至少包含背景、输入材料、目标、边界、章节设计、解释规则等章节

**Step 5: Commit**

```bash
git add docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md
git commit -m "docs: capture capability analysis design"
```

### Task 3: 写入研发/架构向功能分析文档

**Files:**
- Create: `docs/algorithm-platform-function-analysis.md`

**Step 1: 先写核心结论与能力域**

```text
- 双运行态部署
- 统一计算引擎
- 统一 DAG 编排
- 统一 Python 算子
- 消息可靠性与稳定性
```

**Step 2: 将原文映射到平台职责**

Run: `rg "^## |^### " docs/algorithm-platform-function-analysis.md`
Expected: 出现按能力域组织的章节，而非仅按原文顺序罗列

**Step 3: 写入技术映射和模块划分**

```text
- 原文技术要素 -> 平台角色
- 平台模块 -> 研发职责
- 明确哪些内容是推导而非原文直接给出
```

**Step 4: 写入约束与待澄清事项**

Run: `rg "待澄清|非功能要求|约束" docs/algorithm-platform-function-analysis.md`
Expected: 文档中明确提示能力边界，避免把未定义内容当成既定方案

**Step 5: Commit**

```bash
git add docs/algorithm-platform-function-analysis.md
git commit -m "docs: add algorithm platform function analysis"
```

### Task 4: 交付前复核

**Files:**
- Modify: `docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md`
- Modify: `docs/plans/2026-03-17-algorithm-platform-capability-analysis-docs-plan.md`
- Modify: `docs/algorithm-platform-function-analysis.md`

**Step 1: 核对三份文档是否形成闭环**

```text
- 设计记录解释为什么这样写
- 计划文档解释怎样完成
- 功能文档给出最终研发可读结论
```

**Step 2: 运行内容检查**

Run: `git diff -- docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md docs/plans/2026-03-17-algorithm-platform-capability-analysis-docs-plan.md docs/algorithm-platform-function-analysis.md`
Expected: 仅包含本次新增文档内容

**Step 3: 确认中文输出与可追溯性**

```text
- 全文使用中文
- 明确引用源文件
- 明确原文明确与平台化归纳的区别
```

**Step 4: 进行最终文件存在性校验**

Run: `Get-ChildItem docs, docs/plans`
Expected: 能看到本次新增的 3 份文档

**Step 5: Commit**

```bash
git add docs/plans/2026-03-17-algorithm-platform-capability-analysis-design.md docs/plans/2026-03-17-algorithm-platform-capability-analysis-docs-plan.md docs/algorithm-platform-function-analysis.md
git commit -m "docs: add algorithm platform capability analysis package"
```
