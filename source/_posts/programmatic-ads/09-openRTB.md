---
title: 程序化广告 (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记
date: 2026-06-14
categories:
  - 程序化广告
tags:
  - 广告
  - 学习笔记
  - OpenRTB
  - 协议
description: 
  - OpenRTB 2.5 协议 & Native Ads Spec 学习笔记
---

## 一、OpenRTB 是什么

OpenRTB（Open Real-Time Bidding）是由 IAB Tech Lab 制定的**实时竞价通信协议**，定义了 SSP/ADX 与 DSP 之间竞价请求（Bid Request）和竞价响应（Bid Response）的标准 JSON 格式。

它解决的核心问题：不同公司的 SSP 和 DSP 能互相对接，不用每家定义一套私有格式——就像 HTTP 之于 Web，OpenRTB 是程序化广告的"通用语言"。

### 版本演进

| 版本 | 时间 | 关键变化 |
|------|------|----------|
| 1.0 | 2011-02 | 最初的移动端 RTB 规范 |
| 2.0 | 2011-06 | 统一 Display + Video + Mobile |
| 2.3 | 2014 | 新增 Native 广告支持 |
| 2.4 | 2016 | 新增 Audio 广告支持 |
| **2.5** | **2016** | **当前最主流版本**：Header Bidding、billing/loss 通知、Flex Ads、impression metrics 等 |
| 2.6 | 2022+ | Ad Pods（CTV）、结构化 User-Agent、持续增量更新 |

本文重点讲 **2.5**，因为海外广告行业绝大多数交易所和 DSP 都基于这个版本对接。

### 传输协议

- 基础协议：**HTTP POST**（请求体是 JSON）
- 数据格式：**JSON**（也可选 Protobuf/Avro 等二进制格式，部分大厂内部链路会用 Protobuf 提升性能）
- 版本标识：HTTP Header `x-openrtb-version: 2.5`
- 推荐启用 HTTP Keep-Alive 和 gzip 压缩

### HTTP 状态码约定

| 状态码 | 含义 |
|--------|------|
| 200 | 正常返回（有出价） |
| 204 | No Bid（不出价，无响应体） |
| 400 | 请求格式错误 |

---

## 二、Bid Request（竞价请求）

SSP/ADX 向 DSP 发出的请求，描述"这里有一个广告展示机会，你要不要出价、出多少"。

### 对象层级结构

```
BidRequest
├── id                    # 请求唯一 ID
├── imp[]                 # 展示机会（可以有多个）
│   ├── id                # 展示位 ID
│   ├── bidfloor          # 底价
│   ├── bidfloorcur       # 底价币种（默认 USD）
│   ├── banner            # Banner 广告参数
│   ├── video             # 视频广告参数
│   ├── audio             # 音频广告参数
│   ├── native            # 原生广告参数（见 Native Spec）
│   ├── pmp               # 私有交易市场
│   │   └── deals[]       # Deal 列表
│   └── instl             # 是否插屏（0=否，1=是）
├── site / app            # 流量来源（网站 or App，二选一）
│   ├── id / bundle       # 站点 ID / App 包名
│   ├── name              # 名称
│   ├── domain            # 域名
│   ├── cat[]             # 内容类别（IAB 分类）
│   └── publisher         # 发布者信息
├── device                # 设备信息
│   ├── ua                # User-Agent
│   ├── ip                # IP 地址
│   ├── geo               # 地理位置
│   ├── make / model      # 设备制造商 / 型号
│   ├── os / osv          # 操作系统 / 版本
│   ├── ifa               # 广告标识符（IDFA/GAID）
│   ├── dnt               # Do Not Track（0/1）
│   ├── connectiontype    # 网络类型（WiFi/4G/5G...）
│   └── devicetype        # 设备类型（手机/平板/CTV...）
├── user                  # 用户信息
│   ├── id                # 用户 ID（交易所侧）
│   ├── buyeruid          # 用户 ID（DSP 侧）
│   ├── gender            # 性别
│   ├── yob               # 出生年份
│   └── geo               # 用户地理位置
├── regs                  # 法规信号
│   ├── coppa             # 是否受 COPPA（儿童隐私）约束
│   └── ext.gdpr          # GDPR 标志
├── source                # 请求来源（Header Bidding 相关）
├── at                    # 拍卖类型（1=一价，2=二价，默认2）
├── tmax                  # 最大超时时间（ms）
├── wseat[]               # 允许竞价的 Seat 白名单
├── bseat[]               # 禁止竞价的 Seat 黑名单
├── cur[]                 # 允许的出价币种
├── bcat[]                # 屏蔽的广告类别
├── badv[]                # 屏蔽的广告主域名
└── bapp[]                # 屏蔽的 App 包名
```

### 核心对象详解

#### BidRequest（顶层）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 请求唯一标识，贯穿整个链路 |
| imp | object[] | 是 | 至少 1 个 Impression 对象 |
| site | object | 推荐 | 网站流量用 site（与 app 二选一） |
| app | object | 推荐 | App 流量用 app（移动场景主要用这个） |
| device | object | 推荐 | 设备信息 |
| user | object | 推荐 | 用户信息 |
| at | integer | 默认 2 | 拍卖类型：1=一价，2=二价 |
| tmax | integer | 推荐 | DSP 最大响应时间（ms），超时视为 no bid |
| cur | string[] | - | 允许的出价币种，默认 ["USD"] |

> **`id` 就是这次拍卖的 traceId**：由 SSP/ADX 每次请求临时生成、全局唯一（通常是 UUID / 雪花 ID）。Bid Response 必须回填相同的 id（`BidResponse.id == BidRequest.id`），nurl/burl/lurl 也用 `${AUCTION_ID}` 宏带回它，整条链路（请求 → 出价 → 中标 → 计费 → 埋点）靠它串联追踪。注意和 `imp.id` 是包含关系：一次请求一个 `BidRequest.id`，内部可含多个 `imp.id`。

#### Imp（展示机会）

一个 BidRequest 可以包含多个 Imp，每个 Imp 代表页面/App 上的一个广告位。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 展示位 ID，Response 里的 Bid 通过 impid 关联 |
| bidfloor | float | 默认 0 | 底价（CPM），出价低于此值会被拒 |
| bidfloorcur | string | 默认 USD | 底价币种 |
| banner | object | - | Banner 广告（尺寸 w/h、支持的格式等） |
| video | object | - | 视频广告（MIME、时长、协议等） |
| native | object | - | 原生广告（详见 Native Spec 部分） |
| instl | integer | 默认 0 | 是否插屏广告（0=否，1=是） |
| tagid | string | - | 广告位标签 ID |
| secure | integer | - | 是否要求 HTTPS 素材（0=否，1=是） |
| pmp | object | - | 私有交易市场信息 |

**banner/video/native 至少出现一个**，告诉 DSP 这个展示位接受什么类型的广告。

**`id` vs `tagid`：别搞混这两个广告位标识**

两者都跟"广告位"有关，区别在于**作用域**和**生命周期**：

| | `imp.id` | `imp.tagid` |
|---|---|---|
| 谁生成 | SSP 临时生成 | 媒体/SSP 预先配置 |
| 范围 | 单次请求内唯一 | 跨请求长期稳定 |
| 给谁用 | 用于请求 ↔ 响应的技术关联 | 给 DSP 做定向 / 报表 / 出价 |
| 类比 | 排队取的"号码牌" | 店铺的"门牌号" |

- **`imp.id`（展示位 ID）**：仅在**当前这一次 BidRequest 内部**有效，用来区分同一个请求里的多个 Imp（比如一个页面上顶部 banner + 信息流原生，编号 "1"、"2"）。它是一次性的，核心用途是**关联响应**——DSP 在 Bid Response 里用 `bid.impid` 指回是给哪个 Imp 出的价。

```json
// Request
"imp": [
  { "id": "1", "banner": {} },
  { "id": "2", "native": {} }
]
// Response
"bid": [
  { "impid": "1", "price": 2.5 }  // 这一口价是给 imp.id=1 的
]
```

- **`imp.tagid`（广告位标签 ID）**：**跨请求稳定存在**，是媒体侧某个具体广告位的"身份证"。比如"App 首页信息流第 3 屏的那个广告位"永远是同一个 tagid，无论被请求多少次。DSP 用它来做**定向、出价决策、统计报表**（如"对 tagid=home_feed_01 出更高价"，或按 tagid 统计填充率 / eCPM）。

打个比方：`imp.id` 像去银行取的排队号（办完就作废），`imp.tagid` 像固定窗口的编号（永远是 3 号窗口）。

> 补充：`imp.ext` 里有时也会带媒体自定义的 placement/slot ID，概念上与 `tagid` 类似，但属于各家私有扩展约定，非标准字段。

#### Device（设备信息）

DSP 用这些信息做用户定向和出价决策。

| 字段 | 类型 | 说明 |
|------|------|------|
| ua | string | User-Agent 字符串 |
| ip | string | IPv4 地址 |
| geo | object | 地理位置（经纬度、国家、城市） |
| make | string | 设备制造商（如 "Samsung"） |
| model | string | 设备型号（如 "Galaxy S24"） |
| os | string | 操作系统（如 "Android"） |
| osv | string | 系统版本（如 "15"） |
| ifa | string | 设备广告标识符（iOS=IDFA，Android=GAID），用户画像的核心标识 |
| dnt | integer | Do Not Track（1=用户开启了隐私保护） |
| lmt | integer | Limit Ad Tracking（1=用户限制广告追踪） |
| devicetype | integer | 1=手机，2=PC，4=手机，5=平板，7=CTV |
| connectiontype | integer | 0=未知，2=WiFi，4=蜂窝-未知，6=4G，7=5G |

> **`ifa` 是"设备身份证"，不是"广告位 ID"**：它挂在 `device` 下（不是 `user` 下），标识的是**整台设备**——iOS 上是 IDFA、Android 上是 GAID。它**跨 App、跨请求长期稳定**，所以 DSP 才能用它做用户画像、跨应用频控、归因和重定向（retargeting）。这点和前面那些标识正好形成对比：
>
> | 标识 | 范围 | 标识对象 |
> |---|---|---|
> | `BidRequest.id` | 单次请求 | 这次拍卖 |
> | `imp.tagid` | 某个广告位 | 这个版位 |
> | `device.ifa` | 整台设备 | 这个人 / 这台设备 |
>
> **隐私**：用户可重置 ifa 或关闭个性化广告；当 `dnt`/`lmt`=1 时 ifa 可能为空或全 0。iOS 14.5 后的 ATT 框架要求 App 取得授权才能拿到 IDFA，这也是海外流量里大量 ifa 缺失的主因，因此现在常见 hashed ifa 或 Privacy Sandbox / UID2 等替代方案。

#### App（应用信息）—— 移动场景的主要对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | App 在交易所的 ID |
| bundle | string | 包名（如 com.example.store） |
| name | string | App 名称 |
| storeurl | string | 应用商店链接 |
| cat | string[] | 内容类别（IAB 分类） |
| publisher | object | 发布者信息（id, name, domain） |
| ver | string | App 版本 |

#### User（用户信息）

描述这次展示机会背后的"人"，DSP 用它做人群定向、画像匹配。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 交易所侧的用户 ID |
| buyeruid | string | DSP 侧的用户 ID |
| gender | string | 性别（M / F / O） |
| yob | integer | 出生年份（Year of Birth） |
| keywords | string | 兴趣关键词（逗号分隔） |
| geo | object | 用户地理位置 |
| data | object[] | 第三方数据段（DMP 人群标签等） |

**`user.id` vs `user.buyeruid`：两个用户 ID 的区别**

它们都标识"同一个人"，但分属交易所和 DSP **两套不同的账本**，靠 Cookie Matching（ID 映射）打通：

| | `user.id` | `user.buyeruid` |
|---|---|---|
| 归属 | **交易所/SSP** 侧的用户 ID | **DSP** 侧的用户 ID |
| 谁维护 | 交易所自己的用户体系 | DSP 自己的用户体系 |
| 怎么来的 | 交易所识别用户后填入 | 交易所通过 ID 映射表查到"这个人在该 DSP 那边叫什么"后填入 |
| 给谁用 | 交易所内部识别 | DSP 用它在自己库里查画像 / 重定向名单 |

- **为什么需要两个**：交易所和 DSP 各自有一套用户标识体系，同一个人在两边 ID 不同。交易所提前和 DSP 做 **Cookie Matching**（线下/异步建立 `交易所ID ↔ DSP ID` 的映射表），竞价时交易所把对应的 DSP 侧 ID 填进 `buyeruid`，DSP 拿到后就能直接在自己库里查到这个人的画像和重定向名单。
- **和 `device.ifa` 的关系**：在 App 环境里，跨 App 稳定的 `ifa` 往往比 cookie 更可靠，所以移动端常以 `ifa` 为主、`buyeruid` 为辅；Web 环境则更依赖 `user.id`/`buyeruid` 这套 cookie 映射。

#### PMP & Deal（私有交易市场）

PMP 允许媒体和特定买家之间进行预先协商的交易。

| 字段 | 类型 | 说明 |
|------|------|------|
| pmp.private_auction | integer | 1=仅 deal 内的买家可竞价 |
| pmp.deals[] | object[] | Deal 列表 |
| deal.id | string | Deal ID（双方预先协商） |
| deal.bidfloor | float | 该 Deal 的底价 |
| deal.at | integer | 拍卖类型（1=一价固定价，2=二价，3=固定价） |
| deal.wseat | string[] | 允许参与该 Deal 的 Seat |

#### Seat（买方席位）

上面 `deal.wseat` 以及请求顶层的 `wseat`/`bseat` 都用到了 **Seat**，这里统一说明。

**Seat = 买方席位**，代表 DSP 平台里的**一个具体买家身份**——通常是一个广告主或代理商账户。一个 DSP 同时服务很多广告主，给每个买家分配一个 Seat ID，竞价时用它告诉交易所"**这口价是我平台上哪个买家出的**"。

```
DSP（如 The Trade Desk）
├── seat "1001"  → 广告主 A
├── seat "1002"  → 广告主 B
└── seat "1003"  → 代理商 C
```

正因如此，Bid Response 的结构是 `seatbid[]`（按席位分组）→ 每个 `seatbid` 含 `seat` + 该买家的 `bid[]`，同一次响应里 DSP 可以代表多个 Seat 同时出价。

| 字段 | 位置 | 作用 |
|------|------|------|
| `seatbid.seat` | Response | 标明这组出价属于哪个买家 |
| `wseat[]` | Request 顶层 | 白名单：只允许这些 Seat 竞价 |
| `bseat[]` | Request 顶层 | 黑名单：禁止这些 Seat 竞价 |
| `deal.wseat[]` | Request（Deal 内） | 该 Deal 只允许这些 Seat 参与 |

**和 ifa/user 的区别**：`ifa`/`user` 标识"**谁看广告**（受众，流量侧）"，`seat` 标识"**谁买广告**（买家，需求侧）"。

---

## 三、Bid Response（竞价响应）

DSP 返回给 SSP/ADX 的响应，表示"我愿意出这个价买这次展示"。

### 对象层级结构

```
BidResponse
├── id                    # = BidRequest.id（必须一致）
├── bidid                 # DSP 生成的响应 ID
├── cur                   # 出价币种
├── seatbid[]             # 按 Seat 分组的出价
│   ├── seat              # Seat ID（广告主/代理商）
│   └── bid[]             # 具体出价列表
│       ├── id            # 出价 ID
│       ├── impid         # 对应 BidRequest 中的 Imp.id
│       ├── price         # 出价（CPM）
│       ├── adid          # 广告 ID
│       ├── adm           # 广告素材（HTML/VAST/Native JSON）
│       ├── adomain[]     # 广告主域名
│       ├── crid          # 素材 ID
│       ├── w / h         # 素材宽高
│       ├── dealid        # 如果是 Deal 交易，对应 Deal.id
│       ├── nurl          # Win Notice URL（中标通知）
│       ├── burl          # Billing Notice URL（2.5 新增）
│       └── lurl          # Loss Notice URL（2.5 新增）
└── nbr                   # No Bid 原因码（不出价时）
```

### 核心字段说明

#### BidResponse（顶层）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 必须等于 BidRequest.id |
| seatbid | object[] | 是（如果出价） | 至少包含 1 个 SeatBid |
| cur | string | 默认 USD | 出价币种 |
| nbr | integer | - | No Bid 原因码（见下表） |

#### Bid（单个出价）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | DSP 为这个出价生成的唯一 ID |
| impid | string | 是 | 对应请求中的 Imp.id |
| price | float | 是 | 出价（CPM，单位由 cur 决定） |
| adm | string | - | 广告素材标记（HTML/VAST XML/Native JSON） |
| nurl | string | - | Win Notice URL，中标后 SSP 调用通知 DSP |
| burl | string | - | Billing URL（2.5 新增），实际计费时调用 |
| lurl | string | - | Loss URL（2.5 新增），未中标时调用 |
| adomain | string[] | - | 广告主域名，用于品牌安全检查 |
| crid | string | - | 素材 Creative ID |
| dealid | string | - | 如果响应某个 Deal，填对应 Deal.id |
| w | integer | - | 素材宽度（像素） |
| h | integer | - | 素材高度（像素） |

#### No Bid 原因码（nbr）

| 值 | 含义 |
|----|------|
| 0 | 未知错误 |
| 1 | 技术错误 |
| 2 | 无效请求 |
| 3 | 已知爬虫/非人流量 |
| 4 | 可疑非人流量 |
| 5 | 云/代理/VPN IP |
| 6 | 不支持的设备 |
| 7 | 屏蔽的发布者/广告位 |
| 8 | 不匹配的用户 |
| 10 | 广告质量/安全 |

---

## 四、Win / Billing / Loss 通知（2.5 重点新增）

2.5 版本把"中标"和"计费"拆成了两个独立事件：

```
DSP 出价 → SSP 选出赢家
  │
  ├── nurl（Win Notice）：告诉 DSP"你赢了"，DSP 更新竞价算法
  │
  ├── burl（Billing Notice）：广告真正展示/被看到后，SSP 通知 DSP"开始计费"
  │     （2.5 新增，解决"赢了但没展示"的差异）
  │
  └── lurl（Loss Notice）：告诉 DSP"你没赢"，并附上原因
        （2.5 新增，帮 DSP 优化出价策略）
```

### 替换宏（Substitution Macros）

nurl/burl/lurl 中可以包含宏，SSP 在调用时替换为实际值：

| 宏 | 替换为 |
|----|--------|
| ${AUCTION_ID} | BidRequest.id |
| ${AUCTION_BID_ID} | BidResponse.bidid |
| ${AUCTION_IMP_ID} | Imp.id |
| ${AUCTION_SEAT_ID} | Seat ID |
| ${AUCTION_AD_ID} | Ad ID |
| ${AUCTION_PRICE} | 成交价（加密或明文） |
| ${AUCTION_CURRENCY} | 成交币种 |
| ${AUCTION_LOSS} | 未中标原因码 |
| ${AUCTION_MIN_TO_WIN} | 赢得拍卖所需的最低出价（2.5 新增） |

---


## 五、OpenRTB Native Ads Spec（原生广告规范）

### 什么是原生广告

原生广告（Native Ads）是一种**外观和体验都"伪装"成内容、融入 App 内容流**的广告形式——信息流里的卡片、推荐列表里的推荐项、应用商店里的"猜你喜欢"等，看起来和周围的真实内容长得一样，不像横幅那样一眼就是广告。

**和其他广告形式的本质区别，在于"谁来决定长什么样"：**

| 广告形式 | 素材传输方式 | 渲染方 | 外观 |
|---------|------------|--------|------|
| **Banner / 插屏** | 一整块 HTML / 图片 | 广告方已排好版，媒体直接嵌入 | 固定样式，与内容割裂，"一看就是广告" |
| **Video** | VAST/VPAID 视频标签 | 播放器统一渲染 | 视频贴片 |
| **Native（原生）** | **拆散成一个个"零件"**（标题、图片、描述、评分、CTA 按钮…）传过去 | **媒体 App 端**按自己的内容样式重新拼装渲染 | 跟着内容流走，融入无缝 |

关键就在最后一行：原生广告**不传一整块成品素材**，而是把广告拆成结构化的"零件"（assets）。因为每个 App 的信息流卡片长得都不一样（圆角、字号、按钮颜色、图片比例……），只有让媒体端拿到原始零件、用自己的 UI 组件去渲染，才能做到"看起来就是这个 App 的原生内容"。这也是 Native Spec 存在的根本原因——它要约定好"有哪些零件、每个零件的规格"，买卖双方才能对上。

**和动态创意优化（DCO）/ 千人千面的关系：**

正因为原生广告是"零件化"的，它天然适合做 **DCO（Dynamic Creative Optimization，动态创意优化）**——也就是常说的"**千人千面**"：

- 传统 Banner 是一张做好的图，所有人看到的都一样，想换内容只能重新出图。
- 原生广告每个零件（标题文案、主图、价格、CTA 文字）都是独立字段，DSP 完全可以**根据 Bid Request 里的用户画像（`device.ifa`/`user` 等）实时组装不同的零件组合**：给爱好运动的人配运动鞋主图 + "限时 5 折"，给数码用户配手机主图 + "以旧换新"，落地页也能因人而异。
- 同一个广告位、同一条广告计划，**不同用户看到的标题、图片、卖点各不相同**——这就是千人千面。Native Spec 1.2 进一步加了 `assetsurl`/`dcourl` 等字段，专门支持这种由 DSP 侧动态拉取、实时拼装创意的模式。

一句话：**原生广告把素材拆成零件 → 零件可以按人组装 → 于是有了千人千面的 DCO**。三者是层层递进的因果关系。

Native Spec 是 OpenRTB 的**子协议**，专门定义原生广告请求和响应的结构。当前主流版本是 **1.2**（2017 年发布），支持：动态创意优化（DCO）、第三方广告服务、事件追踪、隐私标志。

### Native 在 OpenRTB 中的位置

```
BidRequest
└── imp[]
    └── native              # Native Object
        ├── request         # Native 请求的 JSON 字符串（或直接对象）
        ├── ver             # Native Spec 版本（如 "1.2"）
        └── api[]           # 支持的 API 框架
```

Native 请求内容放在 `imp.native.request` 字段里，可以是 JSON 编码的字符串或直接对象（取决于交易所实现）。

### Native 请求对象层级

```
NativeRequest
├── ver                   # 版本（"1.2"）
├── context              # 内容上下文类型（新闻/社交/产品...）
├── contextsubtype       # 上下文子类型
├── plcmttype            # 展示位类型（信息流/推荐/...）
├── plcmtcnt             # 同时展示的原生广告数量
├── seq                  # 当前是第几个（用于竞价频控）
├── aurlsupport          # 是否支持 assetsurl 响应（0/1）
├── durlsupport          # 是否支持 dcourl 响应（0/1）
├── privacy              # 是否支持隐私链接（0/1）
├── assets[]             # 素材需求列表（核心）
│   ├── id               # 素材 ID
│   ├── required         # 是否必填（0/1）
│   ├── title            # 标题需求
│   │   └── len          # 最大长度
│   ├── img              # 图片需求
│   │   ├── type         # 图片类型（1=Icon, 3=主图）
│   │   ├── w / wmin     # 宽度 / 最小宽度
│   │   └── h / hmin     # 高度 / 最小高度
│   ├── video            # 视频需求（遵循 OpenRTB Video 对象）
│   │   └── mimes, minduration, maxduration, protocols...
│   └── data             # 数据需求
│       ├── type         # 数据类型（见下表）
│       └── len          # 最大长度
└── eventtrackers[]      # 事件追踪需求（1.2 新增）
    ├── event            # 事件类型（1=impression, 2=MRC50...）
    └── methods[]        # 追踪方式（1=img pixel, 2=JS）
```

### 素材（Asset）是什么

> 💡 直观理解：你刷 App 列表（信息流、推荐流）时，偶尔会冒出一条**和其他内容长得几乎一样、只是角落标了广告 / Sponsored**的卡片——那就是原生广告。它之所以能和周围内容无缝融合，靠的就是"素材拆成零件"。

广告行业里"素材"有两个层级的词，别混：

- **Creative（创意/成品）**：一整条完整的广告物料。Banner 里就是一张做好的图（对应 `bid.crid`/`bid.adm`）。
- **Asset（素材零件）**：Native 特有，指把一条 Creative**拆开后的单个组成部分**——一个标题、一张主图、一句描述、一个评分各是一个 asset。

所以原生广告里：**一条 Creative = 一堆 Asset 拼起来**。

```
原生广告卡片（一条 Creative）
├── asset: 标题   "Acme 旗舰 Pro 限时优惠"
├── asset: 主图   [一张 1200×627 的图]
├── asset: 描述   "旗舰影像，全新芯片"
├── asset: 评分   ★ 4.5
└── asset: CTA    "立即下载"
```

要拆成零件，是因为媒体 App 端要用自己的 UI 重新拼装渲染（见上一节），必须拿到拆散的素材而不是成品。

**为什么会有 rating、likes、price 这么多 data 类型？** 因为原生广告要伪装成 App 里的真实内容，"真实内容"长什么样，广告就得能提供对应的零件：

| 场景 | 列表里真实内容长这样 | 原生广告需要的 data 零件 |
|------|---------------------|------------------------|
| 应用商店 / 下载类 | 图标、星级、下载量、"安装" | `rating`、`likes`、`downloads`、`ctatext` |
| 电商 / 购物 | 商品图、原价、促销价、"购买" | `price`、`saleprice`、`ctatext` |
| 本地生活 / O2O | 店名、地址、电话、评分 | `address`、`phone`、`rating` |
| 内容资讯流 | 标题、来源、摘要 | `sponsored`、`desc` |

举例：下载广告若出现在应用商店推荐流里，旁边真实 App 都带着"★4.5、100万+下载"，广告也得填上 `rating`、`downloads`，**否则一看就和周围不一样，"原生"就破功了**。所以下面这张 `data.type` 表，本质是一份**信息流卡片里可能出现的字段清单**——把现实中各类列表会用到的元素标准化编号，买卖双方按编号对接。

### Asset 中的 Data 类型（data.type）

| type 值 | 名称 | 说明 | 示例 |
|---------|------|------|------|
| 1 | sponsored | 赞助商/品牌名 | "Acme" |
| 2 | desc | 描述文字 | "全新旗舰系列..." |
| 3 | rating | 评分 | "4.5" |
| 4 | likes | 点赞数 | "1.2k" |
| 5 | downloads | 下载量 | "100万+" |
| 6 | price | 价格 | "¥3999" |
| 7 | saleprice | 促销价 | "¥2999" |
| 8 | phone | 电话 | "400-xxx" |
| 9 | address | 地址 | - |
| 10 | desc2 | 补充描述 | - |
| 11 | displayurl | 显示 URL | "example.com" |
| 12 | ctatext | CTA 按钮文字 | "立即下载" |

### Image 类型（img.type）

| type 值 | 名称 | 说明 | 推荐尺寸 |
|---------|------|------|----------|
| 1 | Icon | 应用图标 | 最小 50x50 |
| 2 | Logo | 品牌 Logo（已弃用） | - |
| 3 | Main | 主图 | 建议宽高比约 1.91:1（如 1200x627） |

### Native 响应对象层级

DSP 返回的原生广告素材，放在 Bid.adm 字段里（JSON 格式）：

```
NativeResponse
├── ver                   # 版本
├── link                  # 点击行为（整体默认）
│   ├── url              # 落地页 URL
│   ├── clicktrackers[]  # 点击追踪 URL 列表
│   └── fallback         # 备用 URL
├── imptrackers[]        # 曝光追踪 URL（即将弃用，用 eventtrackers 代替）
├── jstracker            # JS 追踪（即将弃用）
├── privacy              # 隐私页面 URL
├── eventtrackers[]      # 事件追踪（1.2 推荐方式）
│   ├── event            # 事件类型
│   ├── method           # 追踪方式（1=img, 2=JS）
│   └── url              # 追踪 URL
├── assetsurl            # 素材托管 URL（1.2 新增，替代内联）
├── dcourl               # 动态创意 URL（1.2 新增）
└── assets[]             # 素材内容（与请求的 asset.id 一一对应）
    ├── id               # 对应请求中的 asset.id
    ├── required         # 是否必需
    ├── title            # 标题
    │   └── text         # "Acme 旗舰 Pro"
    ├── img              # 图片
    │   ├── url          # 图片 URL
    │   ├── w            # 宽度
    │   └── h            # 高度
    ├── video            # 视频
    │   └── vasttag      # VAST XML
    ├── data             # 数据
    │   ├── label        # 显示标签（可选）
    │   └── value        # 值
    └── link             # 该素材独立的点击行为（覆盖顶层 link）
```

### 追踪（Tracking）：从 clicktrackers/imptrackers 到 eventtrackers

原生广告展示后，DSP 需要知道"广告**有没有被看到、有没有被点击**"，用来计费、统计、优化。这就是**埋点追踪**。做法是：DSP 在响应里塞一些**追踪 URL**，媒体端在对应事件发生时去**请求一下这些 URL**，请求到达 DSP 服务器就等于上报了一次事件。

**早期（1.0/1.1）是按"事件种类"各开一个字段：**

| 字段 | 追踪什么 | 怎么触发 |
|------|---------|---------|
| `link.clicktrackers[]` | **点击**事件 | 用户点广告时，媒体逐个请求这些 URL（点击至今仍用它） |
| `imptrackers[]` | **曝光**事件 | 广告渲染出来时，媒体请求这些 URL（一串图片 URL） |
| `jstracker` | 曝光/可见性等 | 一段 **JavaScript 代码**（不是 URL），媒体把它注入页面执行 |

所以最初确实是：**曝光走 `imptrackers`、点击走 `clicktrackers`、需要跑脚本的走 `jstracker`**——三种东西、三个字段、形态还不统一（前两个是 URL 数组，后一个是 JS 字符串）。

**`jstracker` 是什么、为什么要它？** 单纯请求一个图片 URL 只能上报"我被加载了"，但**测不了"广告是否真的出现在屏幕可视区域、停留了多久"**（即"可见性 Viewability"）。这种判断需要在客户端跑代码（监听滚动、计算曝光面积），所以早期单开一个 `jstracker` 字段塞一段 JS。

**1.2 改成统一的 `eventtrackers[]`，用 `event` + `method` 两个维度来区分：**

```json
"eventtrackers": [
  { "event": 1, "method": 1, "url": "https://dsp/imp?id=abc" },   // 曝光，用 img
  { "event": 2, "method": 2, "url": "https://dsp/viewable.js" }   // MRC可见曝光，用 JS
]
```

- `event`：**追踪什么事件**（1=impression 普通曝光、2=MRC 可见曝光-50%、3=MRC 可见曝光-100%、4=视频播放… 点击仍走 `link.clicktrackers`）
- `method`：**用什么方式追踪**（1=img、2=JS）

这样一个数组就涵盖了过去 `imptrackers` + `jstracker` 的所有场景，新增事件类型只要加个 `event` 枚举值即可，不用再开新字段。所以 `imptrackers`/`jstracker` 被标记为**即将弃用**，新实现统一用 `eventtrackers`。

**`method`：img 像素 vs JS 追踪有什么区别？**

| | `method=1`（img 像素） | `method=2`（JS 追踪） |
|---|---|---|
| 形态 | 一个 URL，媒体用一个 1×1 透明图 `<img>` 去加载它 | 一个 URL，媒体用 `<script>` 加载并执行 |
| 能力 | **只能上报"事件发生了"** | 能在客户端**跑逻辑**：测可见性、停留时长、反作弊、采集环境信息 |
| 开销/风险 | 极轻、几乎无安全风险 | 重，且能执行任意脚本，有安全/性能顾虑，App 内 WebView 才好用 |
| 典型用途 | 普通曝光、计费打点 | Viewability 可见性测量、第三方监测（如 MOAT、IAS） |

一句话：**img 像素是"打个卡说我发生了"，JS 是"派个探针上去实地测量"**。简单计数用 img 就够，需要判断可见性/反作弊才上 JS。

### Native 请求/响应示例

**请求**（SSP 告诉 DSP：我需要一个标题 + 一张主图 + 一段描述 + 品牌名）

```json
{
  "ver": "1.2",
  "context": 1,
  "plcmttype": 4,
  "assets": [
    { "id": 1, "required": 1, "title": { "len": 90 } },
    { "id": 2, "required": 1, "img": { "type": 3, "wmin": 600, "hmin": 314 } },
    { "id": 3, "required": 0, "data": { "type": 2, "len": 200 } },
    { "id": 4, "required": 1, "data": { "type": 1 } }
  ],
  "eventtrackers": [
    { "event": 1, "methods": [1, 2] }
  ]
}
```

**响应**（DSP 返回填好的素材）

```json
{
  "ver": "1.2",
  "link": {
    "url": "https://store.example.com/flagship",
    "clicktrackers": ["https://dsp.example.com/click?id=abc"]
  },
  "eventtrackers": [
    { "event": 1, "method": 1, "url": "https://dsp.example.com/imp?id=abc" }
  ],
  "assets": [
    { "id": 1, "title": { "text": "Acme 旗舰 Pro - 限时优惠" } },
    { "id": 2, "img": { "url": "https://cdn.example.com/flagship.jpg", "w": 1200, "h": 627 } },
    { "id": 3, "data": { "value": "旗舰影像，全新芯片加持" } },
    { "id": 4, "data": { "value": "Acme" } }
  ]
}
```

---

## 六、拍卖引擎视角的重点字段

从 SSP 侧拍卖引擎开发的角度，日常最关注的字段：

### 构造 Bid Request 时

| 关注点 | 对应字段 | 为什么重要 |
|--------|---------|-----------|
| 请求标识 | id | 全链路追踪（traceId） |
| 广告位信息 | imp.id, imp.tagid, imp.bidfloor | 决定发给哪些 DSP、底价多少 |
| 广告类型 | imp.banner / video / native | 告诉 DSP 接受什么格式 |
| 超时控制 | tmax | 拍卖引擎的超时阈值 |
| 设备 + 用户 | device, user | 传给 DSP 做定向 |
| 拍卖类型 | at (1=一价, 2=二价) | 决定计价策略 |
| Deal 交易 | imp.pmp.deals | PDB/PD/PMP 私有交易 |

### 解析 Bid Response 时

| 关注点 | 对应字段 | 为什么重要 |
|--------|---------|-----------|
| 出价金额 | bid.price | 选赢家、算 eCPM |
| 素材内容 | bid.adm | 返给客户端渲染 |
| 广告主信息 | bid.adomain | 品牌安全检查 |
| Deal 关联 | bid.dealid | 判断是否走 Deal 价格 |
| 中标通知 | bid.nurl | 赢家确定后回调 |
| 计费通知 | bid.burl | 广告展示后回调 |
| 落败通知 | bid.lurl | 通知未中标 DSP 原因 |

---

## 七、各类 ID 含义速查

OpenRTB 链路里 ID 很多，容易混。按"标识对象"和"生命周期"汇总如下：

| ID 字段 | 所属对象 | 标识对象 | 生命周期 | 谁生成 | 核心用途 |
|---------|---------|---------|---------|--------|---------|
| `BidRequest.id` | 请求顶层 | 这一次拍卖 | 单次请求，一次性 | SSP/ADX | 全链路 traceId，Response/通知回填关联 |
| `BidResponse.id` | 响应顶层 | 同上 | 必须 == BidRequest.id | DSP | 校验响应归属 |
| `BidResponse.bidid` | 响应顶层 | 这次响应 | 单次响应 | DSP | DSP 侧日志追踪（`${AUCTION_BID_ID}`） |
| `imp.id` | Imp | 请求内某个广告位 | 单次请求内唯一 | SSP | 与 `bid.impid` 关联出价 |
| `imp.tagid` | Imp | 媒体某个固定版位 | 跨请求长期稳定 | 媒体/SSP | DSP 定向 / 报表 / 出价 |
| `bid.impid` | Bid | 指回某个 imp | 单次响应 | DSP | 标明这口价给哪个 Imp |
| `bid.id` | Bid | 这条出价 | 单次响应 | DSP | DSP 内部唯一标识 |
| `bid.adid` / `bid.crid` | Bid | 广告 / 素材 | 长期 | DSP | 素材管理、品牌安全、报表 |
| `deal.id` | PMP Deal | 一笔私有交易 | 长期（双方预先协商） | SSP/DSP 协商 | 走 Deal 价格与定向 |
| `device.ifa` | Device | **整台设备 / 人** | 跨 App、跨请求长期稳定 | 操作系统 | 用户画像、跨应用频控、归因、重定向 |
| `user.id` | User | 这个人（交易所侧） | 长期 | 交易所/SSP | 交易所内部识别用户 |
| `user.buyeruid` | User | 这个人（DSP 侧） | 长期 | 交易所（经 ID 映射填入） | DSP 查自己库里的画像 / 名单 |
| `app.id` / `site.id` | App/Site | 媒体应用 / 站点 | 长期 | 交易所 | 流量来源识别 |
| `publisher.id` | Publisher | 发布者 | 长期 | 交易所 | 发布者维度统计与黑白名单 |
| `seat` | SeatBid | 买方席位（广告主/代理商） | 长期 | DSP | 标明这组出价来自哪个买家 |

一句话归纳三类：

- **一次性的（请求级）**：`BidRequest.id` / `BidResponse.id` / `bidid` / `imp.id` / `bid.id`，请求结束即失效，用于本次链路的技术关联。
- **长期稳定的资源 ID（媒体侧）**：`imp.tagid` / `app.id` / `site.id` / `publisher.id` / `deal.id`，标识"广告位 / 媒体 / 交易"这些固定资源。
- **长期稳定的身份 ID（用户/设备侧）**：`device.ifa` / `user.id` / `user.buyeruid`，标识"这个人/这台设备"，是定向和归因的根基，也是隐私监管的重点。

---

## 八、参考资料

| 资源 | 链接 |
|------|------|
| OpenRTB 2.5 官方 PDF | https://www.iab.com/wp-content/uploads/2016/03/OpenRTB-API-Specification-Version-2-5-FINAL.pdf |
| OpenRTB 2.6 GitHub（含 2.5 变更记录） | https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md |
| Native Ads Spec 1.2 GitHub | https://github.com/InteractiveAdvertisingBureau/Native-Ads/blob/main/OpenRTB-Native-Ads-Specification-Final-1.2.md |
| Native Ads Spec 1.2 官方 PDF | https://www.iab.com/wp-content/uploads/2018/03/OpenRTB-Native-Ads-Specification-Final-1.2.pdf |
| Google OpenRTB Protobuf 实现 | https://developers.google.com/authorized-buyers/rtb/downloads/openrtb-proto |