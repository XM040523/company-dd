# company-dd — 求职尽调工具包

给「应聘前摸清一家公司」用的可跑链路。所有可达性结论都在 **2026-10-11 实测**，未实测的一律标注。

## 为什么不是单个 GitHub 项目

上一轮筛出来的项目只覆盖单点，且国内工商类爬虫基本停更：

- 企查查 / 天眼查第三方爬虫（`bouxin/company-crawler`、`yanfeng9507/TianYanChaCrawler`）停在 2023 年，接口鉴权早换了。
- 国内没有活跃的看准网 / 脉脉专用仓库。
- 没有任何项目做到「输入公司名 → 输出完整档案」。

所以链路是拼的：**官方 MCP 拿工商与风险 + 免费接口拿上市公司公告 + 浏览器拿口碑 + Agent 工作流出报告**。

## 数据源可达性（实测）

| 源 | 结果 | 说明 |
|---|---|---|
| 巨潮资讯 cninfo | ✅ 无需认证 | JSON 接口直接可用，本包 `cninfo.py` 已封装 |
| 天眼查官方 MCP | ✅ 端点存活 | `https://mcp.tianyancha.com/mcp` 返回 401（缺 Authorization，即需 OAuth），162 个业务工具 |
| 企查查 MCP | ✅ 端点存活 | `agent.qcc.com` 正常，有 DSH 专用 OAuth 插件 |
| 看准网 kanzhun.com | ⚠️ 首页 200 | 搜索路由重定向回首页，数据要登录 + 浏览器渲染 |
| 牛客 / 脉脉 / offershow | ⚠️ 首页 200 | 同上，走浏览器自动化 |
| 国家企业信用信息公示系统 gsxt.gov.cn | ❌ 521 | 源站拒绝，需真实浏览器 |
| 信用中国 creditchina.gov.cn | ❌ 412 | WAF 挑战 |
| Glassdoor | ❌ 403 | 需真实浏览器 |
| Crunchbase / OpenCorporates API | ⚠️ 401 | 需自行注册 key |

## 三层拼装

**L1 工商 / 风险 / 知产 / 董监高**（最稳，需 OAuth 授权）
- 企查查 MCP：6 个 SERVER（company / risk / ipr / operation / history / executive），个人账号 5 个、企业认证 6 个
- 天眼查官方 MCP：L0 实体锚定 → L1 六面总览 → L2 下钻 → L3 专项，162 工具，官方建议只给 LLM 暴露 7 个（L0+L1）

**L2 上市公司公告**（免费，本包）
- `cninfo.py`：主体检索 + 公告全文检索 + PDF 下载
- 求职视角的检索词：`欠薪`、`劳动仲裁`、`诉讼`、`回购`、`股权激励`、`裁员`、`行政处罚`

**L3 招聘与口碑**
- `eatmoreduck/boss-zhipin-scraper`（1540★，2026-09）：CDP 复用已登录浏览器，输出明文薪资 + 技能词频
- `speedyapply/JobSpy`（4448★）：海外站职位
- `Viy1204/recruiting-copilot`（85★）：Boss直聘 + 猎聘双通道寻源（招聘方视角，可反推岗位真实画像）
- 看准 / 脉脉 / 牛客 / offershow：走 `browser-automation` skill（Playwright）

**L4 技术栈**
- `rverton/webanalyze`（1187★，Go）：批量扫官网技术栈，面试谈资

**L5 报告与面试**
- `Angel2518975237/captain-ai`（3★，2026-09）：**DSH 上的求职公司筛查多智能体工作流**，可恢复、证据严格审查、逐项可追溯，正是本场景的成品形态
- `soreavis/research-entity`（1★）：23 段式尽调 dossier 模板，跨源交叉验证 + 红旗扫描
- `ufiredong/dsh-interviewer`（1★）：模拟面试 + 按证据推导薪资区间

## 接入命令

DSH CLI 路径（本机实测）：

```bash
DSH="/Applications/DeepSeek Harness.app/Contents/Resources/runtime/cli/bin/dsh"
```

企查查 MCP（OAuth，token 存 `~/.dsh/storages`，0700）：

```bash
"$DSH" plugin --profile desktop add qcc-dsh-mcp-oauth
# 重启 DSH，然后在对话里说「连接企查查」触发授权
```

天眼查官方 MCP：

```bash
npm install -g tyc-cli
tyc login                    # 浏览器 OAuth
tyc login --no-block         # 或：打印授权 URL + 6 位验证码，网页授权后 tyc login --resume
tyc init --authorization "YOUR_API_TOKEN"   # 已有 OpenAPI token 时
```

> 沙箱内执行上述命令会报 `EPERM: package.json.lock`——文件沙箱只允许写工作区。请在真实终端跑，或直接在 DSH 的 dshmarket 插件市场里搜「企查查」一键安装。

## 求职尽调流程

1. **定主体**：确认公司全称与统一社会信用代码，别把同名子公司搞混。
2. **查上市状态**：`python3 cninfo.py search 公司简称`，有代码就走 L2 全文检索。
3. **扫风险信号**：`python3 cninfo.py ann 欠薪`、`ann 劳动仲裁`、`ann 诉讼 --since 2025-01-01`。
4. **拉工商与股权**：企查查 / 天眼查 MCP 查实控人、参保人数、经营异常、被执行。
5. **看在招岗位**：`boss-zhipin-scraper` 抓岗位与薪资带宽，判断是扩招还是收缩。
6. **听内部人**：看准 / 脉脉 / 牛客，重点看近半年、同岗位、反复出现的吐槽。
7. **出报告**：按 `dd-template.md` 填，或用 `captain-ai` 跑完整工作流。

## 本包文件

- `cninfo.py` — 巨潮免费接口客户端（无第三方依赖，Python 3 标准库）
- `dd-template.md` — 求职尽调报告模板

## cninfo.py 已知边界

- 只覆盖**上市及挂牌公司**，非上市公司查不到。
- `stock`（精确限定公司）与 `seDate` 不能同时下发——服务端会返回空。脚本在 stock 场景改成本地按日期过滤。
- `seDate` 必须是完整区间，`2025-01-01~` 这类半开写法返回空。脚本自动补齐另一端。
- 数据是公告原文，PDF 需自行下载解析；`fetch` 子命令已实现。
