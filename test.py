import time
import logging
import os
import pyautogui
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

def get_chromium_options(browser_path: str, arguments: list) -> ChromiumOptions:
    """
    Configures and returns Chromium options.
    
    :param browser_path: Path to the Chromium browser executable.
    :param arguments: List of arguments for the Chromium browser.
    :return: Configured ChromiumOptions instance.
    """
    options = ChromiumOptions().auto_port()
    options.set_paths(browser_path=browser_path)
    for argument in arguments:
        options.set_argument(argument)
    return options

def locate_and_click_button(button_image_path: str, timeout: int = 10, confidence: float = 0.8) -> bool:
    """
    定位并点击指定图片的按钮
    
    :param button_image_path: 按钮图片的路径
    :param timeout: 超时时间(秒)
    :param confidence: 图像匹配的置信度 (0-1)
    :return: 是否成功点击
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 增加confidence参数提高匹配准确度
            location = pyautogui.locateOnScreen(button_image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center.x, center.y)
                logging.info(f'成功点击按钮: {button_image_path}')
                return True
        except pyautogui.ImageNotFoundException:
            time.sleep(0.5)
    logging.warning(f'未能找到按钮: {button_image_path}')
    return False

def main():
    # Chromium Browser Path
    isHeadless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    if isHeadless:
        from pyvirtualdisplay import Display

        display = Display(visible=0, size=(1920, 1080))
        display.start()

    browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    
    # Windows Example
    # browser_path = os.getenv('CHROME_PATH', r"C:/Program Files/Google/Chrome/Application/chrome.exe")

    # Arguments to make the browser better for automation and less detectable.
    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu",
        "-accept-lang=en-US",
    ]

    options = get_chromium_options(browser_path, arguments)

    # Initialize the browser
    driver = ChromiumPage(addr_or_opts=options)
    try:
        logging.info('导航到演示页面')
        driver.get('https://nopecha.com/demo/cloudflare')

        # 使用PyAutoGUI处理Cloudflare验证
        logging.info('开始Cloudflare绕过')
        
        # 主要尝试点击button2.png
        if locate_and_click_button('src/button2.png', timeout=15):
            time.sleep(2)  # 等待动画完成
            logging.info("验证完成!")
        else:
            # 如果button2.png未找到，尝试其他按钮
            logging.warning("未找到主要验证按钮，尝试备用按钮")
            if locate_and_click_button('src/button1.png', timeout=5):
                time.sleep(2)
                logging.info("使用备用按钮验证完成!")
            else:
                logging.error("所有验证按钮均未找到")

        logging.info("页面标题: %s", driver.title)
        time.sleep(5)
    except Exception as e:
        logging.error("发生错误: %s", str(e))
    finally:
        logging.info('关闭浏览器')
        driver.quit()
        if isHeadless:
            display.stop()

if __name__ == '__main__':
    main()
