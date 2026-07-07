---
title: 'Java基础(23) | SQL 进阶语法：常用函数、CTE 与窗口函数'
date: 2026-05-23
abbrlink: 23
tags:
  - SQL
  - MySQL
  - 窗口函数
  - 数据分析
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

后端开发不只是写 Java——日常排查问题、给数据团队对账、写报表统计，都离不开 SQL。尤其是广告系统里"统计某个广告主最近 30 天的曝光转化率""按渠道排名找出 Top 10 投放计划"这类需求，光靠 `SELECT * FROM ... WHERE ...` 是不够的。这篇文章整理 MySQL 里常用的函数、CTE（公共表表达式）和窗口函数——后者是写统计类 SQL 最关键的工具。

<!-- more -->

## 1. 常用函数

| 函数功能 | 函数名 | 使用方式 | 返回值 |
|---|---|---|---|
| 求时间/日期差 | `TIMEDIFF` / `DATEDIFF` | `TIMEDIFF(time1, time2)` / `DATEDIFF(date1, date2)` | 时间 / 天数 |
| 时间转换为秒数 | `TIME_TO_SEC` | `TIME_TO_SEC(time)` | 整数 |
| 拼接字符串 | `CONCAT` | `CONCAT(str1, str2, str3, ...)` | 字符串 |
| 带分隔符拼接（类似 Python 的 join） | `CONCAT_WS` | `CONCAT_WS(separator, str1, str2, ...)` | 字符串 |
| 求最大值 / 最小值 | `GREATEST` / `LEAST` | `GREATEST(num1, num2, ...)` | 数字 |
| 四舍五入保留小数 | `ROUND` | `ROUND(num, 2)` | 浮点数 |
| 格式化日期 | `DATE_FORMAT` | `DATE_FORMAT(date, '%Y-%m-%d %H:%i:%s')` | 字符串 |
| 字符串转日期 | `STR_TO_DATE` | `STR_TO_DATE(string, format)` | 日期 |
| 大小写转换 | `UPPER` / `LOWER` | `UPPER(str)` | 字符串 |
| 类型转换 | `CAST` | `CAST(expression AS target_type)` | 目标类型 |
| 返回第一个非 NULL 的值 | `COALESCE` | `COALESCE(expr1, expr2, ...)` | 任意 |
| 日期加减 | `DATE_ADD` / `DATE_SUB` | `DATE_ADD(date, INTERVAL n DAY)` | 日期 |

几个容易用错或者用法不直观的，单独说明一下：

### TIMEDIFF vs DATEDIFF

`DATEDIFF(date1, date2)` 只算**天数差**，忽略时间部分；`TIMEDIFF(time1, time2)` 算的是**时间差**（格式 `HH:MM:SS`），两个参数必须是同类型（都是 time 或都是 datetime）：

```sql
SELECT DATEDIFF('2026-05-20', '2026-05-18');  -- 2（天）
SELECT TIMEDIFF('2026-05-20 10:00:00', '2026-05-20 08:30:00');  -- 01:30:00
```

### DATE_FORMAT：格式化占位符

| 占位符 | 含义 | 示例 |
|---|---|---|
| `%Y` | 4 位年份 | 2026 |
| `%m` | 2 位月份 | 05 |
| `%d` | 2 位日期 | 20 |
| `%H` | 24 小时制小时 | 14 |
| `%i` | 分钟 | 30 |
| `%s` | 秒 | 00 |

```sql
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');  -- 2026-05-20 14:30:00
SELECT DATE_FORMAT(NOW(), '%Y年%m月');            -- 2026年05月
```

`STR_TO_DATE` 是反过来的操作——把字符串按指定格式解析成日期类型，常用于处理"日期被当成字符串存进表"的历史数据：

```sql
SELECT STR_TO_DATE('2026/05/20', '%Y/%m/%d');  -- 2026-05-20
```

### CONCAT vs CONCAT_WS

`CONCAT` 直接拼接，任意一个参数是 `NULL`，整个结果就是 `NULL`；`CONCAT_WS`（WS = With Separator）会自动忽略 `NULL` 参数，并在非空参数之间插入分隔符：

```sql
SELECT CONCAT('a', NULL, 'b');           -- NULL（整体失效）
SELECT CONCAT_WS('-', 'a', NULL, 'b');   -- a-b（自动跳过 NULL）
```

### COALESCE：处理 NULL 的默认值

返回参数列表中第一个非 `NULL` 的值，常用于"给可能为空的字段一个默认值"：

```sql
-- nickname 为空时显示 username，username 也为空时显示 "匿名用户"
SELECT COALESCE(nickname, username, '匿名用户') AS display_name FROM users;
```

### CAST：类型转换

```sql
SELECT CAST('123' AS SIGNED);        -- 123（字符串转整数）
SELECT CAST(3.789 AS DECIMAL(5,2));  -- 3.79（保留 2 位小数）
SELECT CAST('2026-05-20' AS DATE);   -- 2026-05-20（字符串转日期）
```

### DATE_ADD / DATE_SUB：日期加减

```sql
SELECT DATE_ADD('2026-05-20', INTERVAL 7 DAY);   -- 2026-05-27
SELECT DATE_SUB('2026-05-20', INTERVAL 1 MONTH); -- 2026-04-20
SELECT DATE_ADD(NOW(), INTERVAL -30 DAY);        -- 30 天前（负数 = SUB）
```

## 2. CTE：用 WITH 语句拆分查询

复杂查询如果写成一层套一层的子查询，会很难读、很难调试。**CTE（Common Table Expression，公共表表达式）** 用 `WITH ... AS (...)` 把每一步查询命名成一个临时结果集，后面的查询可以直接引用它，就像引用一张表：

```sql
WITH result AS (
    SELECT
        MAX(DATE(start_time)) AS max_date
    FROM
        tb_user_video_log
),
join_table AS (
    SELECT
        tag,
        if_retweet
    FROM
        tb_user_video_log AS t
        INNER JOIN tb_video_info AS i ON t.video_id = i.video_id,
        result
    WHERE
        DATEDIFF(result.max_date, start_time) < 30
)

SELECT
    tag,
    SUM(if_retweet) AS retweet_cnt,
    ROUND(SUM(if_retweet) / COUNT(*), 3) AS retweet_rate
FROM
    join_table
GROUP BY
    tag
ORDER BY
    retweet_rate DESC;
```

逐步拆解这个例子：

1. **`result`**：先算出整张日志表里最新的一天 `max_date`——后面"最近 30 天"都以这一天为基准，而不是 `NOW()`（因为测试数据可能不是今天的）。
2. **`join_table`**：把日志表和视频信息表 join 起来，拿到每条记录的 `tag`（视频标签）和 `if_retweet`（是否转发）。这里 `FROM ... , result` 用逗号把单行的 `result` 也接进 `FROM` 列表——因为 `result` 只有一行一列，这相当于把 `max_date` 这个值"广播"到每一行，方便在 `WHERE` 里用 `DATEDIFF(result.max_date, start_time) < 30` 筛选"最近 30 天"的数据。
3. **最外层查询**：基于 `join_table`，按 `tag` 分组，统计每个标签的转发数 `retweet_cnt` 和转发率 `retweet_rate`。

好处：每个 CTE 都可以单独拿出来跑，看中间结果对不对——比如先单独执行 `result`，确认 `max_date` 算对了，再执行 `join_table`，逐步排查，比一整条嵌套子查询好调试得多。

## 3. CASE 与 IF

### CASE：多分支条件

```sql
CASE if_follow
    WHEN 2 THEN -1
    ELSE if_follow
END
```

等价于"如果 `if_follow` 等于 2，结果为 -1，否则结果就是 `if_follow` 本身"。`CASE` 还有不带表达式、直接写条件的形式：

```sql
CASE
    WHEN score >= 90 THEN '优秀'
    WHEN score >= 60 THEN '及格'
    ELSE '不及格'
END AS level
```

### IF：单分支条件（MySQL 专有函数）

```sql
IF(condition, true_value, false_value)
```

`IF` 是 `CASE WHEN ... THEN ... ELSE ... END` 的简写，只能写一个条件，适合简单的二选一场景：

```sql
SELECT IF(score >= 60, '及格', '不及格') AS result FROM exams;
```

## 4. 窗口函数

> 参考：[通俗易懂的学会：SQL窗口函数](https://www.zhihu.com/tardis/zm/art/92654574?source_id=1005)

`GROUP BY` 分组后，每组只能输出一行——明细数据没了。但很多统计需求是"既要看每一行的明细，又要算出这一行在所在分组里排第几名 / 和上一行比变化了多少"。**窗口函数**就是为这类需求设计的：它不会减少行数，而是在每一行旁边多算一列"基于某个窗口范围的统计值"。

```sql
<窗口函数> OVER (
    PARTITION BY <用于分组的列名>
    ORDER BY <用于排序的列名>
    <ROWS/RANGE 子句>
)
```

- `PARTITION BY`：把数据分成多个"窗口"（类似 `GROUP BY`，但不会合并行）
- `ORDER BY`：决定窗口内行的顺序（影响排名、LAG/LEAD 等函数的结果）
- `ROWS/RANGE` 子句：进一步限定"当前窗口"包含哪些行（默认是整个分区）

窗口函数原则上只能写在 `SELECT` 子句中。

### 4.1 专用窗口函数：排名类

| 函数 | 行为 | 示例（值相同时） |
|---|---|---|
| `ROW_NUMBER()` | 为每一行分配唯一的连续序号，**不管值是否相同** | 1, 2, 3, 4 |
| `RANK()` | 相同值排名相同，**之后的排名会跳号** | 1, 1, 3, 4 |
| `DENSE_RANK()` | 相同值排名相同，**之后的排名不跳号** | 1, 1, 2, 3 |
| `NTILE(n)` | 把结果集尽量平均分成 n 组，返回每行所在的组号 | 8 行分 4 组 → 1,1,2,2,3,3,4,4 |

```sql
SELECT
    name, score,
    ROW_NUMBER() OVER(ORDER BY score DESC) AS row_num,
    RANK()       OVER(ORDER BY score DESC) AS rnk,
    DENSE_RANK() OVER(ORDER BY score DESC) AS dense_rnk
FROM exams;
```

| name | score | row_num | rnk | dense_rnk |
|---|---|---|---|---|
| Alice | 90 | 1 | 1 | 1 |
| Bob | 90 | 2 | 1 | 1 |
| Carol | 85 | 3 | 3 | 2 |
| Dave | 80 | 4 | 4 | 3 |

### 4.2 前后行函数：LAG / LEAD

用于在当前行直接拿到"上一行"或"下一行"的值，常用来计算"环比"（比如本月销量 - 上月销量）：

| 函数 | 作用 | 示例 |
|---|---|---|
| `LAG(column, offset, default)` | 访问当前行**之前**的第 `offset` 行 | `LAG(sales, 1, 0) OVER(PARTITION BY product ORDER BY month)` |
| `LEAD(column, offset, default)` | 访问当前行**之后**的第 `offset` 行 | `LEAD(price, 1) OVER(ORDER BY date)` |

```sql
SELECT
    product, month, sales,
    LAG(sales, 1, 0) OVER(PARTITION BY product ORDER BY month) AS last_month_sales,
    sales - LAG(sales, 1, 0) OVER(PARTITION BY product ORDER BY month) AS diff
FROM monthly_sales;
```

- `offset` 是"往前/往后数几行"，最常用的是 `1`（上一行/下一行）
- `default` 是"如果取不到（比如第一行没有上一行）该返回什么"，这里传 `0` 表示第一个月的环比基准是 0

### 4.3 首尾值函数

| 函数 | 作用 |
|---|---|
| `FIRST_VALUE(column)` | 返回窗口框架中的**第一个**值 |
| `LAST_VALUE(column)` | 返回窗口框架中的**最后一个**值 |
| `NTH_VALUE(column, n)` | 返回窗口框架中的**第 n 个**值 |

```sql
SELECT
    name, dept, salary,
    FIRST_VALUE(salary) OVER(PARTITION BY dept ORDER BY hire_date) AS first_hired_salary,
    NTH_VALUE(salary, 3) OVER(PARTITION BY dept ORDER BY salary DESC) AS third_highest_salary
FROM employees;
```

> **`LAST_VALUE` 的坑**：默认的窗口框架是 `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`（从分区第一行到**当前行**），所以 `LAST_VALUE` 默认取到的其实是"当前行"，不是整个分区的最后一行——想拿到分区真正的最后一行，必须显式指定 `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING`（见 4.5 节）。

### 4.4 聚合窗口函数

`SUM` / `AVG` / `COUNT` / `MIN` / `MAX` 加上 `OVER()` 就变成窗口函数——区别于 `GROUP BY` 里的聚合函数，**它不会把多行合并成一行**：

```sql
SELECT
    name, dept, salary,
    SUM(salary) OVER(PARTITION BY dept) AS dept_total,
    AVG(salary) OVER(PARTITION BY dept) AS dept_avg,
    salary / SUM(salary) OVER(PARTITION BY dept) AS salary_ratio
FROM employees;
```

每一行都能看到自己的明细（`name`、`salary`），同时又能看到所在部门的总和、平均值，以及自己占部门总额的比例——这是 `GROUP BY` 做不到的。

### 4.5 窗口框架规范：ROWS BETWEEN

`ROWS BETWEEN ... AND ...` 进一步限定"当前窗口具体包含哪些行"：

| 关键字 | 含义 |
|---|---|
| `UNBOUNDED PRECEDING` | 分区第一行 |
| `UNBOUNDED FOLLOWING` | 分区最后一行 |
| `CURRENT ROW` | 当前行 |
| `n PRECEDING` | 当前行往前数第 n 行 |
| `n FOLLOWING` | 当前行往后数第 n 行 |

**例 1：累计求和**（从分区第一行累加到当前行）

```sql
SELECT
    id, category, sales_volume,
    SUM(sales_volume) OVER(
        PARTITION BY category
        ORDER BY id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM sales;
```

**例 2：移动平均**（前一行 + 当前行 + 后一行，共 3 行的平均值）

```sql
SELECT
    id, category, sales_volume,
    AVG(sales_volume) OVER(
        PARTITION BY category
        ORDER BY id
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS moving_avg
FROM sales;
```

### 4.6 为什么有时必须用窗口函数代替 GROUP BY

下面这条 SQL 想算"每个商品的利润率"——`profit_price = 1 - 成本价 / 加权平均售价`：

```sql
-- 报错：in_price 既不在 GROUP BY 里，也没被聚合函数包裹
product_profit AS (
    SELECT
        product_id,
        1 - in_price / (SUM(price * cnt) / SUM(cnt)) AS profit_price
    FROM
        join_tb
    GROUP BY
        product_id
)
```

**为什么报错**：SQL 规定 `SELECT` 里出现的每一列，要么在 `GROUP BY` 里，要么被聚合函数（`SUM`/`MAX`/...）包裹。这里 `in_price` 两者都不满足——虽然同一个 `product_id` 对应的 `in_price` 实际上是同一个值（成本价不会按行变化），但数据库不知道这件事，仍然会报错。

**解决方案**：把聚合从"按组合并"换成"窗口聚合"，这样既能用到 `SUM(...) OVER(PARTITION BY product_id)` 算出整个分组的汇总值，又能保留 `in_price` 这种逐行字段，不需要把它也塞进 `GROUP BY`：

```sql
product_profit AS (
    SELECT DISTINCT
        product_id,
        1 - (in_price / (SUM(price * cnt) OVER(PARTITION BY product_id) /
             SUM(cnt) OVER(PARTITION BY product_id))) AS profit_price
    FROM
        join_tb
)
```

`SUM(...) OVER(PARTITION BY product_id)` 会把"该 `product_id` 分组内 `price*cnt` 的总和"算出来，**贴在每一行上**（不合并行），所以 `in_price` 这种逐行字段可以直接拿来用。算完之后每个 `product_id` 会有多行结果（一行对应原表的一行），值都一样，最后用 `SELECT DISTINCT` 去重成一个商品一行。

## 5. 小结

| 主题 | 关键要点 |
|---|---|
| 常用函数 | `DATE_FORMAT`/`STR_TO_DATE` 互为反操作；`CONCAT_WS` 自动跳过 `NULL`；`COALESCE` 取第一个非空值 |
| CTE | `WITH ... AS (...)` 把复杂查询拆成可单独调试的步骤；逗号 + 单行 CTE 可以把一个值"广播"到每一行 |
| CASE / IF | `CASE` 支持多分支，`IF` 是二选一的简写 |
| 排名窗口函数 | `ROW_NUMBER`（不重复）、`RANK`（重复后跳号）、`DENSE_RANK`（重复后不跳号）、`NTILE`（分桶） |
| LAG / LEAD | 取上一行/下一行的值，常用于环比计算 |
| 聚合窗口函数 | `SUM/AVG/COUNT OVER(PARTITION BY ...)`：不合并行，每行都能看到分组汇总 |
| ROWS BETWEEN | 限定窗口范围：累计求和用 `UNBOUNDED PRECEDING AND CURRENT ROW`，移动平均用 `n PRECEDING AND n FOLLOWING` |
| 窗口函数 vs GROUP BY | 当 `SELECT` 里要混用"逐行字段"和"分组聚合值"时，窗口函数 + `SELECT DISTINCT` 比 `GROUP BY` 更合适 |

---

> **下一篇预告**：MySQL 原理与优化——存储引擎、索引、锁与事务隔离级别

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
