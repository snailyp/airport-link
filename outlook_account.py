import asyncio
import json
import os
import random
import string

from pyppeteer import launch

# 扩展目录的路径
EXTENSION_PATH = 'CapSolver.Browser.Extension'

# 配置文件路径
CONFIG_PATH = os.path.join('', 'config.json')


def get_random_string(length=10, use_password_chars=False):
    chars = string.ascii_letters + string.digits
    if use_password_chars:
        chars += "!@#$%^&*()_+<>?/.,;'{}[]\\|~`"
    return ''.join(random.choice(chars) for _ in range(length))


async def type_and_click_next(page, selector, text):
    await page.waitForSelector(selector)
    await page.type(selector, text)
    await page.keyboard.press('Enter')


async def main():
    if not os.path.exists(EXTENSION_PATH):
        print("扩展必须下载并放置在同一文件夹中。检查GitHub上的说明。")
        return

    with open(CONFIG_PATH, 'r') as f:
        config_json = json.load(f)

    if config_json.get('apiKey', '') == '':
        api_key = input("输入apiKey，如果没有则输入'no'：")
        config_json['apiKey'] = api_key
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config_json, f)

    browser = await launch(headless=False, executablePath="C:\Program Files\Google\Chrome\Application\chrome.exe")
    page = await browser.newPage()
    await page.goto('https://signup.live.com/signup')

    email = f"F{get_random_string()}@outlook.com"
    password = get_random_string(20, True)

    await type_and_click_next(page, "#MemberName", email)
    await type_and_click_next(page, "#PasswordInput", password)
    await type_and_click_next(page, "#FirstName", get_random_string())
    await type_and_click_next(page, "#LastName", get_random_string())

    await page.waitForSelector("#BirthMonth")
    await page.click("#BirthMonth")
    await page.keyboard.press('Enter')
    await page.keyboard.press('ArrowDown')

    await asyncio.sleep(0.5)  # 替代C#中的Thread.Sleep

    await page.waitForSelector("#BirthDay")
    await page.click("#BirthDay")
    await page.keyboard.press('Enter')
    await page.keyboard.press('ArrowDown')
    await type_and_click_next(page, "#BirthYear", "2000")

    print(f"电子邮件: {email}")
    print(f"密码: {password}")

    with open("outlook_accounts.txt", "a") as file:
        file.write(f"{email}:{password}\n")
    okButton = "#id__0"
    await page.waitForSelector(okButton)
    await page.click(okButton)
    await page.keyboard.press('Enter')
    await page.close()
    await browser.close()


asyncio.run(main())
