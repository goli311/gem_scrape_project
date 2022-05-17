import time
from PIL import Image
import pytesseract
import base64
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import requests
import scrapy

def get_cookie():
    """selenium part to get cookies"""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        # chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(executable_path='/home/msp/Dhruvil/Training_projects/Git_Testing/gem_scrape_project/gem_scrape_project/chromedriver.exe', options=chrome_options)
        driver.get("https://sso.gem.gov.in/ARXSSO/oauth/doLogin")
        driver.maximize_window()
        # driver.execute_script("alert('...Excecution Started.....');")
        # time.sleep(5)
        # # driver.switch_to.alert.text # output is "qwer"
        # driver.switch_to.alert.accept() # alert closed
        # find the captcha element
        ele_captcha = driver.find_element_by_xpath('//img[@id="captcha1"]')

        # get the captcha as a base64 string
        img_captcha_base64 = driver.execute_async_script("""
            var ele = arguments[0], callback = arguments[1];
            ele.addEventListener('load', function fn(){
              ele.removeEventListener('load', fn, false);
              var cnv = document.createElement('canvas');
              cnv.width = this.width; cnv.height = this.height;
              cnv.getContext('2d').drawImage(this, 0, 0);
              callback(cnv.toDataURL('image/jpeg').substring(22));
            }, false);
            ele.dispatchEvent(new Event('load'));
            """, ele_captcha)

        # save the captcha to a file
        with open(r"captcha_latest.jpg", 'wb') as f:
            f.write(base64.b64decode(img_captcha_base64))

        time.sleep(2)

        filename = "captcha_latest.jpg"
        # Recognize the text as string in image using pytesserct
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        final_text = text.replace('-\n', '')
        print("text", final_text)
        try:
            driver.find_element_by_xpath('//input[@id="loginid"]').send_keys('data.s')
            driver.find_element_by_xpath('//input[@id="captcha_math"]').send_keys(f'{final_text}')
            time.sleep(3)
            driver.find_element_by_xpath('//button[@type="submit"]').click()
            # time.sleep(1)
            driver.find_element_by_xpath('//input[@id="password"]').send_keys('Jintech@7891')
            time.sleep(1)
            driver.find_element_by_xpath('//button[@type="submit"]').click()
            time.sleep(10)
        except Exception as E:
            print("captcha not matched",E)
            driver.quit()
        try:
            ok_click=driver.find_elements_by_xpath('//a[@data-item-id="dialogBtnOk"]')
            for i in ok_click:
                i.click()

            ck = driver.get_cookies()
            print("cookiess...", ck)
            return ck
            # driver.find_element_by_xpath('//a[@id="dLabel"][contains(text(),"Bids")]').click()
            # time.sleep(2)
            # driver.find_element_by_xpath(
            #     '//ul[@class="dropdown-menu multi-level user-details"]/li/a[contains(text(),"List of Bids")]').click()
            # try:
            #     WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) == 2)
            #     print("-------")
            #     # switch windows
            #     driver.switch_to_window(driver.window_handles[1])
            #     # driver.switch_to.window (driver.window_handles[1])
            #     # driver.find_element_by_xpath('//a[@title="Bids"]').click()
            #     # driver.find_element_by_xpath('//a[@title="Bid/RA Status"]').click()
            #
            # except Exception as e:
            #     driver.quit()
            #     print("coudn't find element: ", e)
        except Exception as e:
            driver.quit()
            print("coudn't find element: ",e)

        driver.quit()
    except Exception as E:
        print("error in get_cookie function",E)

    """"""