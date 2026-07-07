"""
CSDN 登录并保存 session 信息
=============================
有头模式打开 CSDN 登录页，等待你手动登录后按回车，
自动保存 cookies 和 localStorage 到 auth.json，
后续脚本可以直接加载复用。
"""

import json
import os
from playwright.sync_api import sync_playwright

AUTH_FILE = os.path.join(os.path.dirname(__file__), "auth.json")
CSDN_LOGIN_URL = "https://passport.csdn.net/login"


def main():
    with sync_playwright() as p:
        # 有头模式启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        page = context.new_page()

        print("正在打开 CSDN 登录页...")
        page.goto(CSDN_LOGIN_URL, wait_until="domcontentloaded")

        print("\n" + "=" * 50)
        print("请在浏览器窗口中完成登录（扫码/密码均可）")
        print("登录成功后，回到这里按 Enter 继续...")
        print("=" * 50 + "\n")

        # 阻塞，等待用户手动登录
        input()

        # 保存完整的 storage state（cookies + localStorage）
        context.storage_state(path=AUTH_FILE)
        print(f"\n✅ 登录信息已保存到: {AUTH_FILE}")

        # 验证一下
        page.goto("https://www.csdn.net/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # 简单检查是否登录成功
        try:
            # 尝试找登录后的用户头像或昵称
            page.wait_for_selector(".user-info, .avatar, .user-name, [class*='login']", timeout=3000)
            print("看起来已登录成功！")
        except Exception:
            print("⚠️  未能确认登录状态，但 session 已保存，后续可重新登录。")

        browser.close()


if __name__ == "__main__":
    main()
