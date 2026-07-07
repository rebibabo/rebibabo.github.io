import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://mp.csdn.net/")
    page.locator(".close-btn").click()
    with page.expect_popup() as page1_info:
        page.get_by_role("link", name="创作").first.click()
    page1 = page1_info.value
    with page1.expect_popup() as page2_info:
        page1.get_by_role("button", name="使用 MD 编辑器").click()
    page2 = page2_info.value
    page2.get_by_text("1. **全新的界面设计** ，将会带来全新的写作体验；").click()
    page2.get_by_text("@[TOC](这里写自定义目录标题) # 欢迎使用").press("ControlOrMeta+a")
    page2.goto("https://editor.csdn.net/md?not_checkout=1&spm=1015.2103.3001.8066&articleId=162665186")
    page2.locator("div").filter(has_text=re.compile(r"^【无标题】$")).click()
    page2.get_by_role("textbox", name="请输入文章标题（5~100个字）").press("ControlOrMeta+a")
    page2.get_by_role("textbox", name="请输入文章标题（5~100个字）").fill("Java高并发底层原理（二十九）—— 从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择")
    page2.get_by_role("button", name="发布文章").click()
    page2.get_by_text("Java高并发", exact=True).click()
    page2.locator("i").nth(2).click()
    page2.locator("i").nth(2).click()
    page2.locator("i").nth(2).click()
    page2.get_by_role("button", name="添加文章标签").click()
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").click()
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill("java")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("CapsLock")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill("java")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("Enter")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("CapsLock")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill("高并发")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("Enter")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill("标签2")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("Enter")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill("标签3")
    page2.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("Enter")
    page2.get_by_role("button", name="关闭").nth(1).click()
    page2.get_by_role("textbox", name="本内容会在各展现列表中展示，帮助读者快速了解内容。若不填，则默认提取正文前256个字。").click()
    page2.get_by_role("textbox", name="本内容会在各展现列表中展示，帮助读者快速了解内容。若不填，则默认提取正文前256个字。").fill("\n上一章讨论的是单机内存版任务处理系统：请求线程把 `Task` 放入有界队列，Worker 从队列中取出任务并执行。这个模型可以解决任务异步化、短暂削峰、有限并发执行的问题，但它还有一个明显边界：任务只存在于 JVM 内存里。\n\n一旦服务重启、机器宕机，或者系统部署成多个实例，内存队列就很难继续保证任务可靠。文件解析任务如果只放在本地队列中，进程一退出，队列里还没执行的任务就会消失；Worker 正在执行到一半的任务，也没有稳定位置记录它到底完成了没有。\n\n本章继续沿用文件解析任务这个例子，讨论任务不能丢")
    page2.get_by_role("textbox", name="无声明").click()
    page2.get_by_text("部分内容由AI辅助生成").click()
    page2.locator(".el-checkbox__inner").click()
    page2.get_by_label("Insert publishArticle").get_by_role("button", name="发布文章").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
