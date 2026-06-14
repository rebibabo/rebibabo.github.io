---
title: 'Java基础(番外) | Git 日常操作实战：从提交到协作全流程'
date: 2026-05-28
tags:
  - Git
  - 版本控制
  - 团队协作
categories:
  - Java基础
---

## 前言

[26 开发规范全集](/2026/05/26/Java-basic/26-dev-conventions/) 里讲过 Git 的"团队规范"——分支怎么命名、commit message 怎么写、PR 模板长什么样。但很多刚入职的同学缺的不是规范，而是**命令本身**：遇到一个具体场景，该敲哪条命令、为什么。

这篇就专门聊操作层面：日常提交、分支协作、冲突解决、撤销回退，全部用"场景 → 命令"的方式来讲，尽量少讲理论。

<!-- more -->

## 1. 核心概念：三个区域 + 一次提交的旅程

理解 Git 最关键的一步，是搞清楚一份代码在提交过程中会经过哪几个"区域"：

```
工作区 (Working Directory)
   │  git add
   ▼
暂存区 (Staging Area / Index)
   │  git commit
   ▼
本地仓库 (Local Repository)
   │  git push
   ▼
远程仓库 (Remote Repository, 如 GitHub/GitLab)
```

| 区域 | 是什么 | 对应命令 |
|---|---|---|
| 工作区 | 你在编辑器里看到、修改的文件 | 直接编辑文件 |
| 暂存区 | "下一次提交将会包含哪些改动"的草稿 | `git add` 加入，`git restore --staged` 移出 |
| 本地仓库 | 你电脑上的 commit 历史 | `git commit` 写入 |
| 远程仓库 | 团队共享的仓库（GitHub/GitLab/Gitee） | `git push` / `git pull` 同步 |

**为什么要有"暂存区"这一层？**

因为你改了 5 个文件，但这次只想提交其中 2 个文件的改动（比如另外 3 个还没改完）。暂存区让你可以**精确挑选**这次 commit 包含哪些改动，而不是"一锤子全部提交"。

## 2. 日常基本操作

### 2.1 初始化与克隆

```bash
# 在已有目录里初始化一个新仓库（很少用，新人多数是 clone）
git init

# 克隆远程仓库到本地
git clone https://github.com/xxx/project.git
```

### 2.2 查看状态与差异

| 命令 | 作用 | 使用场景 |
|---|---|---|
| `git status` | 看哪些文件被修改/新增/删除，分别处于工作区还是暂存区 | 每次操作前先看一眼，养成习惯 |
| `git diff` | 对比"工作区"与"暂存区"的差异 | 看看自己改了啥，还没 add |
| `git diff --staged` | 对比"暂存区"与"上次 commit"的差异 | add 之后，commit 之前再确认一遍 |
| `git diff HEAD` | 对比"工作区+暂存区"与"上次 commit"的差异 | 想看本次所有改动（不管有没有 add） |
| `git log` | 查看提交历史 | 排查"这段代码是谁、什么时候改的" |
| `git log --oneline --graph --all` | 用一行+图形展示所有分支的提交历史 | 看分支结构、合并关系，**强烈建议常用** |

> **小技巧**：`git diff` 系列三个命令的区别，记一个口诀——**"diff 看工作区改动，diff --staged 看暂存区改动，diff HEAD 看全部改动"**。

### 2.3 提交

```bash
git add file1.java file2.java   # 只加这两个文件
git add .                        # 加当前目录下所有改动（小心误加不该提交的文件）
git commit -m "feat: 添加用户注册接口"
```

如果只是想"修改上一次的 commit message"或者"把刚才漏掉的小改动并进上一次 commit"：

```bash
git commit --amend
```

> **注意**：`--amend` 会改写上一次 commit 的哈希值。如果这个 commit **已经 push 到远程**，且别人可能已经拉取过，就不要用 `--amend`，否则会导致历史冲突（后面 rebase 部分会再提一次这个原则）。

## 3. 分支管理

### 3.1 创建、切换分支

```bash
git branch                     # 列出本地所有分支
git branch feature/login       # 创建新分支（不切换过去）
git checkout feature/login     # 切换到该分支
git checkout -b feature/login  # 创建并立即切换（等价于上面两行）

# Git 2.23+ 推荐用 switch / restore 替代 checkout 的部分功能，语义更清晰
git switch feature/login        # 切换分支
git switch -c feature/login     # 创建并切换
```

| 命令 | 历史地位 |
|---|---|
| `git checkout` | 老命令，功能"过载"——既能切换分支，又能恢复文件，容易搞混 |
| `git switch` / `git restore` | 新命令，把"切分支"和"恢复文件"拆成两个职责更清晰的命令 |

新项目可以优先用 `switch`/`restore`，但老项目、老教程里 `checkout` 还是随处可见，**两套都要认识**。

### 3.2 合并分支：fast-forward vs merge commit

假设 `main` 分支没有新提交，你在 `feature/login` 上开发完了，合并回 `main`：

```bash
git switch main
git merge feature/login
```

这时会发生两种情况之一：

**情况一：Fast-forward（快进合并）**

如果 `main` 在你开发期间**没有任何新 commit**，Git 会发现"其实只是把 main 的指针往前移到 feature/login 的最新提交就行了"，不需要产生新的合并节点：

```
合并前:  main ──A──B
                  \
         feature   C──D

合并后:  main ──A──B──C──D
```

**情况二：产生 Merge Commit**

如果 `main` 在你开发期间**也有新 commit**（比如别人合并了别的功能），Git 没办法简单"快进"，会自动创建一个新的"合并提交"，把两条线汇合：

```
合并前:  main ──A──B──────E
                  \
         feature   C──D

合并后:  main ──A──B──────E──M
                  \         /
                   C────────D
```

`M` 就是 merge commit，它有两个父提交（E 和 D）。

### 3.3 删除分支

```bash
git branch -d feature/login        # 删除本地分支（已合并才能删，安全）
git branch -D feature/login        # 强制删除本地分支（未合并也删，危险）
git push origin --delete feature/login  # 删除远程分支
```

## 4. 远程协作

### 4.1 fetch vs pull：很多人搞混的两个命令

| 命令 | 做了什么 | 会不会改动你本地的代码 |
|---|---|---|
| `git fetch` | 只从远程下载最新的提交信息到本地（更新 `origin/main` 这种"远程分支指针"） | **不会**，你的工作区和本地分支完全不变 |
| `git pull` | 等价于 `git fetch` + `git merge`（或 `rebase`，取决于配置） | **会**，会把远程的新提交合并到你当前分支 |

**为什么有时候推荐先 fetch 再 merge，而不是直接 pull？**

因为 `pull` 是"自动合并"，如果远程有新提交且和你本地冲突，会直接在你工作区炸出冲突，打断你的思路。先 `fetch` 看看远程改了什么（`git log origin/main`），再决定要不要合并/怎么合并，会更可控。

不过日常开发中，直接 `git pull` 也完全够用，没必要每次都分两步。

### 4.2 推送到远程

```bash
git push                  # 推送到已关联的远程分支
git push -u origin feature/login  # 第一次推送新分支，-u 设置"上游分支"关联关系
```

设置了 `-u`（即 `--set-upstream`）之后，以后这个分支直接 `git push`/`git pull` 就知道该推到/拉取哪个远程分支了，不用每次都写全 `origin feature/login`。

### 4.3 典型协作流程

```
1. git switch main
2. git pull                     # 同步最新代码
3. git switch -c feature/xxx    # 开新分支开发
4. ... 写代码、commit ...
5. git push -u origin feature/xxx
6. 在 GitHub/GitLab 上发起 PR/MR
7. 代码评审通过后合并到 main
8. git switch main && git pull  # 合并后再同步一次本地 main
9. git branch -d feature/xxx    # 清理本地分支
```

## 5. 合并冲突怎么处理

冲突的本质：**同一个文件的同一处代码，两条分支都改了，Git 不知道该听谁的**。

当 `merge`/`pull`/`rebase` 过程中遇到冲突，Git 会在文件里插入冲突标记：

```java
public void sendNotice() {
<<<<<<< HEAD
    smsService.send(user.getPhone(), "您的订单已发货");
=======
    emailService.send(user.getEmail(), "您的订单已发货");
>>>>>>> feature/email-notice
}
```

- `<<<<<<< HEAD` 到 `=======` 之间：**当前分支（你这边）**的内容
- `=======` 到 `>>>>>>> feature/email-notice` 之间：**被合并进来的分支**的内容

### 解决步骤

1. 打开文件，看清楚两边各改了什么
2. 手动编辑成你想要的最终结果（比如两个通知都发，或者只保留一个），**删除所有 `<<<<<<<`/`=======`/`>>>>>>>` 标记**
3. `git add` 这个文件，标记"冲突已解决"
4. 如果是 `merge`：`git commit` 完成合并；如果是 `rebase`：`git rebase --continue`

```bash
# 解决完所有冲突文件后
git add NoticeService.java
git commit          # merge 场景
# 或
git rebase --continue  # rebase 场景
```

如果发现这次合并太乱，想放弃整个合并过程，回到合并之前的状态：

```bash
git merge --abort     # 放弃 merge
git rebase --abort    # 放弃 rebase
```

## 6. rebase vs merge

这是新人最容易迷惑的一对概念，先看图：

**Merge**：保留两条线的真实历史，会多一个 merge commit。

```
main     ──A──B──────────M
              \          /
feature        C────D────
```

**Rebase**：把 `feature` 分支的提交"重新接到" `main` 最新的提交后面，**历史变成一条直线**，看起来好像 feature 是从最新的 main 上才开始开发的：

```
rebase 前:
main     ──A──B──E
              \
feature        C──D

rebase 后:
main     ──A──B──E
                   \
feature             C'──D'   (C'、D' 是 C、D 的"重写版"，哈希值变了)
```

### 什么时候用哪个？

| 场景 | 推荐 | 原因 |
|---|---|---|
| 把别人最新的 `main` 同步到自己**还没 push** 的功能分支 | `rebase` | 让历史保持线性、干净，方便 review |
| 把功能分支合并回 `main`（团队协作，多人共享分支） | `merge` | 保留真实的协作历史，且不会改写已共享的 commit |
| 个人本地分支整理 commit（比如把 5 个"修bug"的小 commit 合并成 1 个） | `rebase -i`（交互式） | 提交历史更清晰 |

### 黄金原则：不要 rebase 已经 push、且别人可能已经拉取的分支

因为 rebase 会**改写 commit 的哈希值**（上图里的 C → C'）。如果别人已经基于 C 做了开发，你 rebase 之后把 C 变成了 C'，远程历史和别人本地历史就"分叉"了，会导致非常混乱的冲突。

简化记忆：**"自己的、还没分享出去的历史，可以随便 rebase 整理；已经分享给别人的历史，别动它，用 merge。"**

## 7. 撤销与回退

这部分最实用，也最容易出事故。核心思路是：**先看你的改动"走到了哪一步"，再选对应的撤销命令**。

| 场景 | 命令 | 说明 |
|---|---|---|
| 改了文件，还没 `add`，想恢复成上次提交的样子 | `git restore <file>`（旧：`git checkout -- <file>`） | 工作区改动直接丢弃，**慎用，不可恢复** |
| 已经 `add` 了，想撤销 add（但保留改动） | `git restore --staged <file>` | 文件回到"已修改但未暂存"状态 |
| 已经 `commit`，但还没 `push`，想撤销这次提交 | `git reset --soft HEAD^` | 撤销 commit，**改动回到暂存区**，代码不丢 |
| 同上，但想把改动也退回工作区（取消 add） | `git reset --mixed HEAD^`（默认模式） | 撤销 commit + 撤销 add，改动还在工作区 |
| 同上，但想**连改动都丢弃**，完全回到上次提交 | `git reset --hard HEAD^` | **危险**，改动彻底丢失，不可恢复（除非用 reflog） |
| 已经 `push` 到远程，别人可能已经拉取，想撤销 | `git revert <commit>` | **不改写历史**，而是新建一个"反向提交"来抵消之前的改动，安全 |

### reset 三种模式图解

`HEAD^` 表示"上一个提交"。三种模式的区别在于：撤销 commit 之后，**改动内容回到哪一层**：

```
                soft          mixed(默认)      hard
本地仓库(commit)  撤销           撤销            撤销
暂存区            保留改动        清空 ←撤销了add  清空
工作区            保留改动        保留改动 ←代码还在  清空 ←代码丢失
```

- `--soft`：只撤销 commit 这一步，改动还乖乖待在暂存区，**最温和**
- `--mixed`（默认不写参数就是这个）：撤销 commit + 撤销 add，改动回到工作区，文件内容不丢
- `--hard`：连工作区的改动也一起清空，**相当于"穿越回上一次提交的瞬间"**

### reset vs revert：本质区别

- `reset`：**移动 HEAD 指针**，让分支"假装"这次提交没发生过——会改写历史，适合**还没分享出去**的提交
- `revert`：**新增一个提交**，内容是"撤销上一个提交的改动"——不改写历史，历史上仍能看到"做了什么、又撤销了什么"两条记录，适合**已经分享出去**的提交

### reflog：后悔药

如果不小心 `reset --hard` 丢了改动，或者删错了分支，**先别慌**，Git 在一段时间内不会真的删除这些 commit，用 `reflog` 还能找回来：

```bash
git reflog              # 查看所有 HEAD 移动的记录，包括"丢失"的 commit
git reset --hard <hash> # 找到丢失前的那个 commit 哈希，恢复回去
```

> `reflog` 是本地仓库的"操作历史"，记录了 HEAD 曾经指向过的每一个位置，是新手误操作后最值得先尝试的救命命令。

## 8. 暂存与清理

### 8.1 stash：临时收起改动

场景：你正在 `feature/a` 分支改代码，改了一半，突然要切到 `main` 修一个紧急 bug，但当前改动还不想 commit：

```bash
git stash              # 把当前改动"收起来"，工作区恢复干净
git switch main
# ... 修复 bug、提交、push ...
git switch feature/a
git stash pop          # 把刚才收起的改动还原回来
```

| 命令 | 作用 |
|---|---|
| `git stash` | 暂存当前改动 |
| `git stash list` | 查看所有暂存记录（可以暂存多次） |
| `git stash pop` | 恢复最近一次暂存，并从列表中删除 |
| `git stash apply` | 恢复最近一次暂存，但**保留**在列表中（可以多次应用） |

### 8.2 clean：清理未跟踪的文件

场景：本地有一堆构建产物、临时文件（不在 `.gitignore` 里），想一键清理：

```bash
git clean -n     # 先 dry-run，看看会删掉哪些文件（强烈建议先跑这个）
git clean -f     # 真正删除未跟踪的文件
git clean -fd    # 连未跟踪的目录也一起删
```

> **危险操作**：`git clean` 删除的文件**不会进回收站，也不在 Git 历史里**，删了就是真的没了。务必先 `-n` 确认。

## 9. cherry-pick 与 tag

### 9.1 cherry-pick：摘一个 commit 到当前分支

典型场景：`main` 分支上有个 hotfix commit，你的 `release` 分支也需要这个修复，但不想把 `main` 的其他改动也带过来：

```bash
git switch release
git cherry-pick <commit-hash>
```

效果：把指定的那一个 commit 的改动，复制一份应用到当前分支，生成一个新的 commit（哈希值不同，内容相同）。

### 9.2 tag：标记版本

```bash
git tag v1.0.0                  # 给当前 commit 打标签
git tag -a v1.0.0 -m "发布说明"  # 带注释的标签（推荐，可以记录发布信息）
git push origin v1.0.0           # 推送标签到远程
git push origin --tags           # 推送所有标签
```

`tag` 常用于标记"这是某个正式发布的版本"，方便以后快速定位到当时的代码状态。

## 10. 速查表：我想做 X，该敲什么

| 我想... | 命令 |
|---|---|
| 看现在有哪些改动还没提交 | `git status` |
| 看具体改了什么内容 | `git diff` |
| 创建并切换到新分支 | `git switch -c <branch>` |
| 把本地分支推到远程并建立关联 | `git push -u origin <branch>` |
| 同步远程最新代码到当前分支 | `git pull` |
| 把 main 的最新改动同步到我的功能分支（线性历史） | `git rebase main` |
| 撤销最后一次 commit，但代码不丢 | `git reset --soft HEAD^` |
| 撤销已经 push 的某次提交 | `git revert <commit>` |
| 临时切分支但当前改动还没提交完 | `git stash` → 切分支 → `git stash pop` |
| 找回误删的 commit/分支 | `git reflog` |
| 把某个 commit 摘到当前分支 | `git cherry-pick <commit>` |
| 看分支结构和合并关系 | `git log --oneline --graph --all` |

## 11. 小结

| 主题 | 核心要点 |
|---|---|
| 三个区域 | 工作区 → 暂存区 → 本地仓库 → 远程仓库，`add`/`commit`/`push` 分别对应三次"提交" |
| 分支合并 | fast-forward（无新增节点）vs merge commit（产生汇合节点） |
| fetch vs pull | fetch 只下载不合并，pull = fetch + merge |
| rebase vs merge | 没 push 的历史可以 rebase 整理成直线；已分享的历史用 merge，别 rebase |
| 撤销操作 | 没 add 用 `restore`，没 push 用 `reset`，已 push 用 `revert`，丢了用 `reflog` 找 |
| stash/clean | stash 临时收起改动；clean 删除未跟踪文件，操作前务必 `-n` 预览 |

新人入职第一周，把第 2、3、4、5 节的命令练熟（status/diff/commit/branch/merge/pull/push + 解决一次真实冲突），基本就能跟上团队协作的节奏了。第 6、7 节(rebase/reset)可以慢慢用、慢慢理解，**遇到不确定的操作，先 `git status` 看清楚现状，拿不准就先 `git stash` 或者复制一份代码备份再操作**，这样即使搞错了也有退路。
