#!/bin/bash
# ============================================================
# CSDN 定时发布 - macOS 定时任务设置
# ============================================================
# 1. pmset 唤醒 Mac（每天 23:58，即使 sleep 也能醒来）
# 2. launchd 在 00:00 执行发布脚本
# ============================================================

PLIST_NAME="com.csdn.publish"
PLIST_FILE="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNNER="$SCRIPT_DIR/auto-upload/run_publish.sh"

echo "===== CSDN 定时发布设置 ====="

# ── 1. 设置睡眠唤醒 ──
echo ""
echo "1. 设置每天 23:58 自动唤醒 Mac（需管理员密码）..."
sudo pmset schedule cancelall 2>/dev/null
sudo pmset repeat wakeorpoweron MTWRFSU 23:58:00
echo "   ✅ 唤醒计划已设置（每天 23:58）"

# ── 2. 创建 launchd plist ──
echo ""
echo "2. 创建 launchd 定时任务（每天 00:00 执行，caffeinate 防休眠）..."

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$RUNNER</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/auto-upload/schedule.log</string>

    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/auto-upload/schedule.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin</string>
        <key>HOME</key>
        <string>$HOME</string>
        <key>DEEPSEEK_API_KEY</key>
        <string>${DEEPSEEK_API_KEY:-}</string>
    </dict>
</dict>
</plist>
EOF

# ── 3. 加载 launchd ──
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"
echo "   ✅ launchd 已加载"

# ── 4. 验证 ──
echo ""
echo "===== 设置完成 ====="
echo "唤醒计划: $(pmset -g sched | grep wakeorpoweron)"
echo "launchd 状态:"
launchctl list | grep "$PLIST_NAME" && echo "   ✅ 运行中" || echo "   ❌ 未运行"
echo ""
echo "📋 待发布列表: $SCRIPT_DIR/auto-upload/schedule_config.json"
echo "📋 执行日志:   $SCRIPT_DIR/auto-upload/schedule.log"
echo ""
echo "往 schedule_config.json 里加文章即可，每天 00:00 自动发布。"
echo ""
echo "⚠️  确保 DEEPSEEK_API_KEY 已设: export DEEPSEEK_API_KEY=xxx"
echo "⚠️  如需修改唤醒时间: sudo pmset repeat wakeorpoweron MTWRFSU 23:58:00"
echo "⚠️  取消定时: sudo pmset repeat cancel && launchctl unload $PLIST_FILE"
