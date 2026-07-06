---
title: 锁升级
tags:
  - wiki
  - glossary
  - concurrency
  - lock-upgrade
type: glossary
source_series: concurrency
status: seed
---

# 锁升级

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

锁升级是 JDK 1.6 后 `synchronized` 的优化机制：偏向锁 → 轻量级锁 → 重量级锁，根据竞争强度逐步升级，尽可能在低开销状态下解决问题。锁升级是不可逆的（不支持降级）。

## 上下文

三个级别：
- **偏向锁**：假设大多数时候没有竞争，只有一个线程反复进入同步块。对象头记录该线程 ID，进入时检查是否是自己——是则直接通过，不 CAS。
- **轻量级锁**：当偏向锁被另一个线程打破时升级。通过 CAS 将对象头的 Mark Word 替换为指向线程栈中 Lock Record 的指针。竞争失败时短暂自旋等待。
- **重量级锁**：自旋仍失败后升级。线程挂起进入 Monitor 的 Entry Set 等待操作系统调度唤醒。成本最高但能让出 CPU。

核心思想：不是每次都用最重的同步方式，而是让 JVM 根据实际竞争情况自适应选择。

## 相关术语

- [[wiki/glossary/concurrency/synchronized|synchronized]] — 锁升级是 synchronized 的实现优化
- [[wiki/glossary/concurrency/Monitor|Monitor]] — 重量级锁的底层实现
- [[wiki/glossary/concurrency/CAS|CAS]] — 轻量级锁的竞争依赖 CAS

## 深入阅读

- [[wiki/concepts/concurrency/synchronized|synchronized 概念页]]
- [[_posts/concurrency/04-synchronized为什么会影响性能|04-synchronized 为什么会影响性能]]
