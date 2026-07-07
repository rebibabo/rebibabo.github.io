---
title: CMP
tags:
  - wiki
  - glossary
  - programmatic-ads
  - cmp
type: glossary
source_series: programmatic-ads
status: seed
---

# CMP（Consent Management Platform，同意管理平台）

[[wiki/glossary/programmatic-ads/index|返回词汇表]]

## 定义

CMP 是管理用户隐私授权（Consent）的平台。当用户访问网站或 App 时，CMP 弹出的"同意/拒绝 Cookie""同意/拒绝个性化广告"对话框，负责收集和存储用户的授权选择。

## 上下文

在 GDPR（欧盟通用数据保护条例）等隐私法规生效后，CMP 变得不可或缺。广告平台（DSP、DMP、ADX 等）在处理用户数据之前，必须知道用户是否同意被追踪、被画像、被个性化投放。

CMP 收集的授权信息通过 IAB Europe 的 TCF（Transparency & Consent Framework）标准字符串传递给下游广告平台。

## 相关术语

- [[wiki/glossary/programmatic-ads/DMP|DMP]] — DMP 需依据 CMP 授权范围处理数据
- [[wiki/glossary/programmatic-ads/DSP|DSP]] — DSP 竞价时需检查 CMP 授权状态
- [[wiki/glossary/programmatic-ads/定向|Targeting]] — 未获授权时不能做个性化定向

## 深入阅读

- [[wiki/concepts/programmatic-ads/CMP|CMP 概念页（完整版）]]
- [[_posts/programmatic-ads/03-DSP-helper|programmatic-ads (2)：DSP 身边的 4 个帮手——广告服务平台全解]]
