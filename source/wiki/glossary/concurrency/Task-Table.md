---
title: 数据库任务表
tags:
  - wiki
  - glossary
  - concurrency
  - task-table
type: glossary
source_series: concurrency
status: seed
---

# 数据库任务表（Task Table）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

数据库任务表是让内存队列中的任务获得持久化和可恢复性的方案。任务状态写入数据库表，数据库成为任务的事实来源——内存队列降级为执行前缓冲。服务重启后可重新加载未完成任务。

## 上下文

核心流程：提交任务时先 `INSERT` 入库（状态 CREATED），再 `offer` 到内存队列。即使队列满，任务也不丢失——数据库里有记录，后续由定时扫描器重新加载。状态流转：CREATED → RUNNING → SUCCESS / FAILED → RETRYING → RUNNING → SUCCESS / DEAD。

多实例防重复靠状态抢占：`UPDATE ... SET status='RUNNING' WHERE status IN ('CREATED','RETRYING')`。影响行数为 1 表示抢到；为 0 表示已被其他实例抢走。状态抢占尽量避免了重复执行，但不能完全保证——Worker 抢到后宕机任务仍停在 RUNNING。因此还需要业务幂等兜底。

## 相关术语

- [[wiki/glossary/concurrency/MQ|MQ]] — 数据库任务表和 MQ 的选择
- [[wiki/glossary/concurrency/Worker-Model|Worker Model]] — 任务表的消费基础
- [[wiki/glossary/concurrency/Idempotency|幂等]] — 任务表重复执行时的兜底机制

## 深入阅读

- [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统概念页（完整版）]]
- [[_posts/concurrency/29-从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择|29-可靠任务系统]]
