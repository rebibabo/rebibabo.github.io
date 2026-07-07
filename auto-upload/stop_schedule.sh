#!/bin/bash
# ============================================================
# 停止 CSDN 定时发布（清理所有相关进程 + 取消定时）
# ============================================================

echo "===== 停止 CSDN 定时发布 ====="

# 1. 卸载 launchd
echo "1. 卸载 launchd 定时任务..."
PLIST="$HOME/Library/LaunchAgents/com.csdn.publish.plist"
launchctl unload "$PLIST" 2>/dev/null && echo "   ✅ 已卸载" || echo "   ⏭️  未加载"

# 2. 取消 pmset 唤醒
echo "2. 取消 pmset 唤醒计划..."
sudo pmset repeat cancel 2>/dev/null && echo "   ✅ 已取消" || echo "   ⏭️  无唤醒计划"

# 3. 杀掉正在运行的发布相关进程
echo "3. 清理残留进程..."

PATTERNS=(
    "schedule_publish.py"
    "schedule_publish_dummy.py"
    "publish_csdn.py"
    "run_publish.sh"
    "caffeinate.*schedule_publish"
    "chromium.*playwright"
    "Chromium.*headless"
)

for pattern in "${PATTERNS[@]}"; do
    pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill 2>/dev/null
        echo "   ✅ 已终止: $pattern"
    fi
done

echo ""
echo "===== 清理完成 ====="
echo "查看残留: ps aux | grep -E 'publish|playwright|chromium' | grep -v grep"
