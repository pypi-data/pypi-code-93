def web_screenshot(url: str, **kwargs) -> str:
    from playwright.sync_api import sync_playwright
    from datetime import datetime

    print("🤖 : Chromium import is OK...")

    # p = sync_playwright().start()
    # iphone_11 = p.devices["iPhone 11 Pro"]
    # browser_type = p.chromium
    # browser = browser_type.launch(headless=True)

    # print(
    #     '🤖 : Launching browser... Please wait for a while then you will see the result.'
    # )
    # context = browser.new_context(**iphone_11)
    # page = context.new_page()
    # page.set_viewport_size({"width": 375, "height": 635})
    # page.goto(url, wait_until="networkidle")
    # file_name = f'screenshot{datetime.now().strftime("%m-%d_%H:%M:%S")}.png'
    # page.screenshot(path=file_name)
    # page.close()
    # browser.close()

    with sync_playwright() as p:
        iphone_11 = p.devices["iPhone 11 Pro"]
        browser_type = p.chromium
        print("🤖 : Hey, I found the chromium binary...")
        print(browser_type)
        print(
            '🤖 : Launching browser... Please wait for a while then you will see the'
            ' result.'
        )
        browser = browser_type.launch(headless=True)
        context = browser.new_context(**iphone_11)
        page = context.new_page()
        page.set_viewport_size({"width": 375, "height": 635})
        page.goto(url, wait_until="networkidle")
        # page.screenshot(path=f'./example-{browser_type.name}haha.png')
        file_name = f'screenshot{datetime.now().strftime("%m-%d_%H:%M:%S")}.png'
        page.screenshot(path=file_name)
        print(f"🤖 : DONE")
        print(f'The file is at {file_name}')
        browser.close()
    return file_name
