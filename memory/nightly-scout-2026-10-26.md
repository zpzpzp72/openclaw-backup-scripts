# Nightly Scout — 2026-10-26 (memory)

> 详细报告：`heartbeat/nightly-scout-2026-10-26.md`

## 头号事实（可复用）

- **`modelcontextprotocol/servers` v2.1.0（2026-10-25T00:03Z）一次性修 8 个漏洞 / 3 个 server，同日公开 8 条 GHSA（00:15–00:19Z）**。这是本场最重要的信号，远超任何单篇论文。
  - filesystem：GHSA-53mr-w429-c597（父目录 TOCTOU 任意写，**Windows 仅部分修复**）、GHSA-7rgq-gccq-qphx（路径 check/use 不一致，尾部引号绕过）、GHSA-4gxg-m5jx-9j57（大小写变体绕过 symlink 检查，macOS 受影响）、GHSA-hhwq-wxfx-cj7g（list_directory_with_sizes 跟随 symlink 泄露元数据）
  - everything：GHSA-mvf5-2qqv-rg3c（**不校验 Origin + `ACAO: *` → 任意网页可调用工具（如 get-env）并读结果**）
  - fetch：GHSA-v38p-wf49-hx2j（IDNA 主机名 SSRF 绕过）、GHSA-66qx-2266-pmj6（NAT64 `64:ff9b::/96` 前缀当公网，元数据可达）、GHSA-3jqg-r5pp-rmp2（重定向后不再检查 robots.txt）
  - **修复版本**：`@modelcontextprotocol/server-filesystem@2.0.1`、`@modelcontextprotocol/server-everything@2.0.1`、`mcp-server-fetch==2026.10.24`
  - ⚠️ **升级陷阱**：包管理器把 2.0.1 排在所有 2025.x/2026.x 日期版本之后，**不会自动提示升级**，必须显式指定版本安装。

## MCP 生态

- **MCP spec 仍未发版**：最新 tag `2026-07-28`（sha 5f5440b），**连续 10 场 / 90 天**。仓内最后提交 10-23。`governance-wg` 仓 10-19 建立工作组结构 → 发版待治理 WG 与 Tasks WG 收敛。
- **registry 转入纯安全加固**：10-24 单日 9 个安全向提交（ECDSA P-384 签名填充至固定宽度、validators 拒绝非法参数/空位置参数/不完整仓库元数据、GitLab 嵌套子组 URL、init 记录 repository.id 防改名失效、**mcp-publisher 安装器 pin & verify**）。
- **多语言 SDK 安全同步**：Go 限制 HTTP client 跨源重定向（#1440）+ 403 时 `WWW-Authenticate` 带 `insufficient_scope`（#1421）；Swift 转义 `WWW-Authenticate` quoted-pair（#305）+ data URL base64 检测改从 header 读；C# 新增 **SEP-2640 Skills 扩展支持**（#1856）；Ruby 连续修 stdio/HTTP 帧编码；Python 结构化输出支持裸 dict/set、**移除 schema 中生成的 title**（省 token）、修扫描告警；TypeScript token 刷新可选携带 scope（#3085）。
- **版本**：servers v2.1.0（10-25）/ inspector v2.12.0（10-21）/ ts v2.4.0（10-23）/ rust rmcp-v3.7.0（10-22）/ csharp v2.3.0（10-20）/ MCP python v2.3.0（10-02）/ **go v1.8.0（09-14，停滞 41 天）** / anthropic-sdk-python **v2.3.0**（10-23 23:18Z）/ claude-code v2.1.310（10-23 23:39Z）。
- **MCP org 10 月新建 3 仓**：governance-wg(10-19)、experimental-ext-file-uploads(10-14)、experimental-ext-filesystems(10-07)。access 仓用 Pulumi 同步 GitHub Team / Google Workspace / Discord / Cloudflare Access / npm & PyPI 发布权限。

## arXiv

- **周末无新批次**：cs.AI 200 条核验，最新提交日仍 10-22（169/200 为 10-22，31 为 10-21），最新 ID 仍 2610.31667。**本场 arXiv 增量为 0**，转为系统挖掘 cs.MA 25 篇（首次系统性覆盖）。
- **cs.MA 安全/治理 4 篇（最大增量）**：
  - **2610.31446 When Is a Memory Safe Enough to Act On?** — 动作条件化记忆验证：复核需求是**动作的属性**不是记忆的属性；形式化为序贯停止问题；动作后果增大可使同一记忆依次穿过 proceed/verify/direct-abstention；实践门控 **AMV-Guard**。
  - **2610.29669 Conflicted Records (BiasGuard-D)** — typed 对抗契约 + 三模型多数表决；单一 judge 共享偏差不可用。
  - **2610.30221 AAM/5C** — 五能力 × 七层；**R-AUT 分离提议/决定/执行**：治理层签**签名评估证明** → 安全层签**绑定证明的短时效 act token** → 策略执行点双校验。
  - **2610.30557 Steward (Governed Self-Evolution)** — 自我进化边界画在**类型系统**里；9 角色 agent + 七层共享记忆；改进靠每晚复盘打分，季度 reflector 提案由**确定性门控可逆应用** + 输入重放校验。
- **2610.31314 State Integrity Collapse** — 定义模型「记得约束却不再应用」；7 provider 快照 × 5 深度探针，严格联合保持率 62.4%–100.0%；**分叉回溯审计显示 88.6% 失败是行为漂移而非普通遗忘**（剔除脆弱离群后 84.4%）。
- **2610.31325 Chair Personas** — 7 agent 模拟科室，病例原样重放只改主席 persona：写成规则时当场手术率 93%(专断)/2%(回避)/57%(无人格)，但手术决策几乎不变 → **persona 主要改「是否现在做」而非「做什么」**；多轮一致性 ≠ 正确性。
- 其他 cs.MA：2610.30780 ABRA（agent-bound UI，可复用视图绑定任务语义）、2610.30851 ADAPT for Science（引力波探测器设计，匹配预算下平均损失 0.204）、2610.31003 Agri-SCHOLAR（APSIM 当评估 oracle）、2610.30516 LLM 隐写（7,200 条回复中 **168 条解码器漏掉的可验证编码 + 706 条词长/词首模式重建**，E2E 恢复会掩盖区分）。

## 产业安全

- **CVE-2026-111497（"Node2Shell" → "HTTP2Shell"）**：Google Brotli 解码器越界写（1.0.3–1.2.0，全平台），**CVSS 9.2**。**OpenAI 2 月发现、10-23 披露**；10-21 Node.js 披露、10-22 Python 披露、10-23 跨语言确认。补丁覆盖 libbrotli / Python / C++ / Node.js / bun / Envoy（Apache、Nginx 默认不解 Brotli）。HN 365 分 / 182 评论。
- 与 10-21 的 Patch the Planet（PHP）构成**「AI 发现漏洞 → 协调披露 → 生态打补丁」流水线第二次出现**，跨语言扩散仅 2 天。
- Cerebras 万亿参数模型部署工程（HN 282 / 95 评论），与 Kimi K3.1 Pro 同期。
- **GitHub 新仓出现「场景化 MCP 集群」**：麦当劳 MCP 衍生 6+ 独立仓（mcd-party-planner 1,589★、mcd-money-saver 356★、mai-suanpan 220★、mcd-saver-checkup 206★ 等）；另有 earshot（2,754★，让编码 agent 听音）、leanrea（2,480★，8KB skill 替代 REA）、reason-network（1,221★，编码 agent 互聊）。

## 跨源主线判断

1. **「批准必须绑定到具体效果」从论文变成 CVE**：2610.31446（动作条件化验证）+ 2610.29669（对抗契约多数表决）+ 2610.30221（R-AUT 签名证明 + 短时效 token）+ Vercel plan/scope + Go/Swift SDK 把 `insufficient_scope` 写进 `WWW-Authenticate` + servers v2.1.0 八个漏洞 —— **五个独立来源在 24 小时内指向同一句话：授权不是布尔值，是带作用域、带时效、带效果的证明对象**。
2. **MCP 安全重心完全下沉到实现层**：spec 90 天未发版，但 servers 一天修 8 个 CVE、registry 一天 9 个安全提交、5 个 SDK 各修跨源重定向与认证头 —— **协议层停滞，运行时层狂奔**。
3. **Brotli CVE 是「AI 参与攻防」的第一个可量化样本**：2 月发现 → 10-23 披露，跨语言扩散 2 天，7 个运行时同日拿到补丁。
4. **记忆安全三层分工已清晰**：State Integrity Collapse（状态）→ action-conditioned verification（决策）→ AMV-Guard（执行），三篇论文可组合成完整链条而非三个孤立问题。
5. **授权语义正在下沉到 wire format**：Go/Swift 的 `WWW-Authenticate`、TS 的 token 刷新带 scope、Python 移除 schema title 省 token —— **上下文预算与授权精度同时在 SDK 层被优化**。
6. **MCP 正从「协议玩具」变成「应用脚手架」**：垂直行业 MCP 生态自发生成 + 编码 agent 协作类工具（reason-network）与多模态 agent 工具（earshot）同时冒头。

## 工具/运维备忘

- arXiv API 必须用 **https**（`http://export.arxiv.org` 返回 301）。
- **arXiv 周末不发布新批次**：周末场（10-25/26）arXiv 增量为 0，应转为挖掘已释放批次的 cs.MA/其他分类，不要重复报 cs.AI。
- **`graphify cluster-only` 正确用法**：`graphify cluster-only . --graph graphify-out/graph.json`（直接传路径会拼成 `graph.json/graph.json`）。
- **主图增量合并方法**：自建 snapshot → 映射 `file_type` 到 `code|document|image|paper|rationale` → 追加节点（`source_file` 指向本场 corpus、`captured_at` 填 UTC）+ 去重追加边 → 再跑 `cluster-only`。本场 357→504 节点、743→1207 边。
- **Anthropic RSS 4 个候选 URL 全 404**（`/rss.xml`、`/news/rss.xml`、`/feed.xml`、`/news/feed.xml`）；官网 `https://www.anthropic.com/news` 可从 `self.__next_f.push([1,"..."])` 内嵌 JSON 解析 title/date/category（需反斜杠转义还原）。
- **LangChain blog `/rss/` 现返回 Webflow HTML**（非 RSS）。
- **Google AI RSS 旧 URL 需 `curl -L` 跟随 301**（`https://blog.google/innovation-and-ai/technology/ai/rss/`）。
- **`web_fetch` 到 openai.com 会被拦截**（`Blocked: resolves to private/internal/special-use IP address`），OpenAI 原文只能用 RSS 描述字段替代。
- **`web_search` provider 连续 8 天失败**（10-06 → 10-26），需排查 duckduckgo 配置。
