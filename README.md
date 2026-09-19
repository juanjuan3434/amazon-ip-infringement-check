# amazon-ip-infringement-check

> 亚马逊选品侵权排查 SOP —— 给一条 Amazon 链接/ASIN + 目标站点，输出 **0–10 分风险评级 + Claim Chart + 「可做 / 不可做」一句话结论**。

一套用于**跨境电商选品阶段**的知识产权风险排查方法（SOP）与配套脚本集，沉淀自 6 个真实案例（宠物用品 / 家居收纳 / 儿童文具 / 美护个护），当前版本 **v4.8**。

---

## 它解决什么问题

选品时最难回答的不是"这个好不好卖"，而是"**这条链接我能不能卖**"。市面上的侵权预警文章只告诉你"有个专利"，但不告诉你能不能做。本 SOP 的做法是：

1. **把产品拆成技术特征**，去目标国的专利库里逐一比对（Claim Chart 逐要素表）；
2. **判断命中专利的性质**（已授权 / 待审 / 发明 / 外观），因为这决定风险等级和应对方式；
3. **做同款侦察**，用 Amazon 自己的关联商品轮播判断"这是工厂公版货还是克隆品"——这往往比查专利更快、更准；
4. 输出一张**分维度评分表**和一句**可做/不可做**的结论，以及（如果不可做）具体的规避方向。

## 排查边界（重要）

**只查这五项：**

| 维度 | 说明 |
|---|---|
| 发明专利 | 核心。命中即最高危 |
| 外观设计专利 | 核心 |
| 版权 | 限于用户提供的主图/图案 |
| 诉讼 / 维权方 | 权利人主体、执法记录、律所 |
| Amazon 平台风险 | APEX / RAV / 投诉密度 |

**不查（用户自行处理）：** 商标、合规资质、供应链（1688）、自有品牌、视频、产品内部结构。

> 原因：这套流程面向"自有品牌 + 1688 拿货 / ODM 定制"的卖家模式，品牌与合规由卖家自己决策，排查只回答"**有没有专利/版权/诉讼/平台雷**"。

## 安装

> 本仓库已**公开**：任何人可直接 `git clone`，或在 GitHub 页面点 **Code → Download ZIP**（无需账号）。

**方式一：直接给文件夹（推荐，分享给单个同事）**

1. 拿到压缩包（或直接拷这个文件夹）
2. 解压 / 放到技能目录，二选一：
   - **用户级**（推荐，所有项目都能用）：`~/.workbuddy/skills/amazon-ip-infringement-check`
     Windows：`%USERPROFILE%\.workbuddy\skills\amazon-ip-infringement-check`
   - **项目级**（只在某项目生效）：`<项目目录>/.workbuddy/skills/amazon-ip-infringement-check`
3. 确认结构是 `…/amazon-ip-infringement-check/SKILL.md` —— **SKILL.md 必须直接位于该文件夹根下**，不要多套一层目录
4. 重启 WorkBuddy 会话，技能列表里出现 `amazon-ip-infringement-check` 即生效
5. **建议先跑一次环境自检**，确认本机齐活：
   ```bash
   python "<技能目录>/scripts/doctor.py"
   ```
   输出 `结论：核心功能可用 ✅` 即没问题；若有 `[WARN]` 只影响个别脚本，`[FAIL]` 会告诉你缺什么。

**方式二：git clone**（公开仓库，任何人可直接克隆，无需账号或授权）

```bash
git clone https://github.com/juanjuan3434/amazon-ip-infringement-check.git \
  "$HOME/.workbuddy/skills/amazon-ip-infringement-check"
```

Windows：

```powershell
git clone https://github.com/juanjuan3434/amazon-ip-infringement-check.git `
  "$env:USERPROFILE\.workbuddy\skills\amazon-ip-infringement-check"
```

> ⚠️ 用 **Download ZIP** 方式时，GitHub 解压出来的目录名会带 `-main` 后缀（`amazon-ip-infringement-check-main`），**建议重命名**为 `amazon-ip-infringement-check` 再放进技能目录，避免技能名不干净。

**运行环境**：Python 3.9+（绝大多数脚本只用标准库；`pdftext.py` 需 `pypdf`，`cmpside.py` / `decf*.py` / `relimgs*.py` 需 `Pillow`）；`amz.js` / `dl*.js` / `fetch*.js` 需 Node 18+（用内置 fetch，无需装包）。需要能访问 Google Patents / USPTO / FreePatentsOnline 等检索站点。

## 案例数据目录约定（跨机器可移植）

脚本**不写死任何本机路径**，换成别人电脑也能直接跑：

- **工作目录**（放案例的 PDF、图片、输出的文件夹）由环境变量 `IPCHECK_DIR` 指定；**不设则用当前工作目录**。所以最省事的用法是：`cd` 进案例目录再跑脚本，例如 `python <skill>/scripts/sheets.py D1000009 2,3`。
- 脚本之间的互相调用（如 `decf.py` → `decode.py`、各脚本加载 `g4.py`）一律按**脚本自身所在目录**解析，因此技能装在哪个盘、哪个用户名下都不影响。
- 想固定指向某个案例目录，也可以设一次环境变量：
  ```powershell
  $env:IPCHECK_DIR = "D:\cases\bandana"     # 当前会话有效
  ```


## 用法

直接说人话触发，例如：

> 帮我排查一下这个链接在英国和美国能不能做：https://www.amazon.co.uk/dp/XXXXXXXXXX

建议同时给出：**目标站点**（US / UK / 双站）、**产品主图**（Amazon 反爬拿不到主图，需你提供）、以及**已知的拿货来源**（1688 同款 / ODM 定制）。

产出：一份中文 Markdown 报告（十节结构，含分维度评分表、Claim Chart、证据等级表、已查数据源清单、规避方向）。

## 判定主干（一句话记住）

> **先看有没有命中的专利，再看它的性质。**

| 情形 | 可执行性 | 美国 APEX | 综合分锚点 |
|---|---|---|---|
| 已授权**发明专利**命中 | ✅ 可执行 | ✅ 适用（卖家不参与即自动下架） | **9–10 🔴** |
| 已授权**外观专利**命中 | ✅ 可执行 | ❌ 不适用（只能走公开表单，可反申诉） | 5–8 |
| 仅**待审申请** | ❌ 不可执行 | ❌ 不适用 | 不抬分，但必须给"授权后升级预警" |
| 无命中，但同款集群 = 公版货 | — | — | 2–4 🟢 |
| **同款集群 = 克隆品**（背后有原版品牌且高频执法） | ✅ | — | **8–9 🔴** |

**两个最容易判错的地方：**

1. **同款侦察有两种相反结论** —— 多人卖同款**不等于**安全。集群里若有品牌自称 `the original / patented` + 高定价 + `Strictly Enforced`，那这个集群就是权利人的**起诉名单**（对照：蓬松喷雾案 = 真公版 → 4/10 可做；淋巴引流刷案 = 克隆集群 → 9/10 不可做）。
2. **改颜色躲不掉** —— **外观**专利保护视觉（改形改色可绕），**发明**专利保护**结构**（改色/换包装/换营销图完全无效）。

## 目录结构

```
amazon-ip-infringement-check/
├── SKILL.md          方法论主体（v4.8，含六案对照与判定主干）
└── scripts/          31 个可复用脚本
```

## 脚本速查

**先跑这个：环境自检**

| 脚本 | 作用 |
|---|---|
| `doctor.py` | 一键自检：Python 版本 / 脚本是否齐全 / **解码器能否加载** / 工作目录可写 / Node / 可选依赖（PIL、pypdf）。装完先跑一次，缺什么一目了然 |

**Amazon 页面解析**

| 脚本 | 作用 |
|---|---|
| `amz.js` | 页面重试抓取（3 组 UA 轮换 + 8 次重试，>200 KB 才落盘） |
| `x2.py` | 全字段提取（标题/五点/BSR/变体/**patent 字样计数**/图片 key） |
| `detail.py` | 详情字段提取（兼容新旧版式） |
| `ctx.py` | 关键词上下文定位（判断 `patent` 字样属本品还是轮播竞品） |
| `ximgs.py` | 抽全部商品图 + 关联 ASIN 频次（美国站点版） |
| `uimgs.py` | 同上，英国等非美站点版 |
| `mapimg.py` | 关联图 ↔ ASIN 映射 |

**同款侦察（核心手法）**

| 脚本 | 作用 |
|---|---|
| `relimgs.py` | 下载关联商品图 → 拼 contact sheet（一屏目视找同款） |
| `relimgs2.py` | 同款侦察 UK 版（自动把缩略图升到 `_SL400`） |
| `prodimg.py` | 本品全部主/附图拼 montage |
| `evidence.py` | 拼"证据一屏"（本品 + 包装 + 效果图 + 近失专利） |
| `zoom.py` | 产品图裁剪放大 5×（判材质/缝线，避免误判） |

**专利检索与文本**

| 脚本 | 作用 |
|---|---|
| `fetchall.js` | FreePatentsOnline 批量检索 |
| `pfpo.py` | 解析 FPO 检索结果 → 专利号/名称/摘要清单 |
| `h2t.py` | FPO 单篇页 HTML → 纯文本 |
| `fmt.py` | 把 FPO 单行长文本按权项编号断行（读权项必备） |
| `pdftext.py` | **任意专利 PDF 抽文本 + 单独抽权利要求**（EP/WIPO/公开申请），并抽查扉页**指定国/期限/权利人** |

**专利附图取图与解码**

| 脚本 | 作用 |
|---|---|
| `dl.js` / `dl_list.js` / `dl_list2.js` | USPTO 批量下载模板（AbortController 110s 超时 + 4 次重试） |
| `dl_ep.js` | **EPO 公开出版服务**下载模板（EP 授权文本；EP 号后须带国别码） |
| `catalog.py` | 列出 PDF 内所有图像页（先看清再解码） |
| `sheets.py` / `decode.py` | 从专利 PDF 抽指定页图纸 → 解码为 PNG |
| `g4.py` | 纯标准库 **CCITT Group 4 (T.6)** 解码器（被上面两个脚本依赖） |
| `extract.py` / `batch.py` | CCITT 码流抽取（调试用）/ 批量下载解码 |

**并排比对**

| 脚本 | 作用 |
|---|---|
| `decf.py` / `decf2.py` | 批量解码多件专利 → 拼 montage，一次目视 10–15 件 |
| `cmpside.py` | 本产品裁图 vs 候选专利附图并排 |
| `fetch_site.js` | 带浏览器 UA 的站点抓取（权利人官网 / **第三方分销商页** / 案件通报页） |

> **两条流水线别混**：USPTO 的附图是 CCITT 传真位图（用 `decode.py`/`sheets.py`）；EP / WIPO 的正文是文字流 PDF（用 `pdftext.py`）。

## 报告结构（十节）

1. 产品基本信息 → 2. 版权风险 → 3. 发明专利风险 → 4. 专利法律状态 → 5. Claim Chart → 6. 外观设计风险 → 7. 公司主体/维权方 → 8. 历史诉讼 → 9. Amazon 平台风险 → 10. 综合评级与建议

综合风险 ≥7 时追加：最危险专利 + 目标国有效性 + 专利家族 + 独立权利要求逐字 + 具体结构风险点 + **「改颜色无效」对比表** + 规避方向（按推荐度排序）。

## 版本

| 版本 | 主要更新 |
|---|---|
| **v4.8.2** | **公开发布前脱敏**：清除全部 16 处真实 ASIN 与自有品牌名（改为 `B0XXXXXXnn` 占位符，方法论与结论不受影响）；新增 `scripts/doctor.py` 环境自检 |
| **v4.8.1** | **跨机器可移植**：清除全部 14 处写死的本机路径；脚本改为从**自身所在目录**加载 `g4.py` / `decode.py`；工作目录改由 `IPCHECK_DIR` 环境变量或当前目录决定；补全 `name` / `description` 元数据（让技能能被正确识别与触发）；仓库转为**公开**并采用 **MIT** 许可证 |
| **v4.8** | 同款侦察的「公版 vs 克隆集群」二分类；原版权利人溯源 + 权利矩阵穷举；「改颜色躲不掉」判据；EP 授权 + GB 指定读法；EPO 通道 |
| v4.7 | 双市场（US+UK）作业差异；通用品类名抢注；近失专利必须下载核实 |
| v4.6 | 关联商品轮播 = 同款侦察窗口；异形/瓶型外观专利的有限穷尽策略 |
| v4.5 | 专利分层判定框架；APEX 机制细节补全 |
| v4.4 | 已授权发明专利命中时的完整作业流程 |

## 免责声明

本 SOP 及脚本产出的是**公开资料筛查结果**，**不构成律师的法律意见，也不是 FTO（自由实施）分析报告**。所有结论均标注了证据等级（A 公开证据 / B 间接证据 / C 推测），存在无法穷尽的检索路径（如泛化标题的外观专利库）。**涉及重大投入前，请咨询专业知识产权律师。**

## 许可证

本项目采用 **MIT License**，详见 [LICENSE](LICENSE)。可自由使用、修改、再分发（保留版权声明即可）。

---

## English

A practical SOP + 31 scripts for **Amazon product IP-risk screening** at the sourcing stage: given a listing URL and a target marketplace, it produces a 0–10 risk score, a claim chart against the relevant patents, and a go/no-go conclusion. Covers utility & design patents, copyright, litigation/enforcement, and Amazon platform risk (APEX / RAV). Brands, compliance and supply chain are intentionally out of scope.

Built and battle-tested over six real cases. Method notes are written in Chinese.
