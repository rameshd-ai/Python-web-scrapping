from ast import stmt
from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# from mysql.connector import connection
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import date
import csv

# sql connection
# conn = connection.MySQLConnection(
#     host="localhost", database="wave_scrapping", user="root", password=""
# )

options = Options()
options.headless = True


def scrapy(url, file_name, wait_time=40):
    try:
        print("Generating no of pages....")
        # time.sleep(30)

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        # driver.implicitly_wait(10)
        if not wait_time:
            wait_time = 40
        driver.maximize_window()
        driver.get(url)
        print(f"wating for {wait_time} seconds...")
        time.sleep(wait_time)

        # title
        title = driver.title
        # critical_error
        ce = driver.find_elements(By.XPATH, "//li[@id='error']")
        critical_error = [x.find_element(By.TAG_NAME, "span").text for x in ce]

        # contrast_error
        time.sleep(30)
        co = driver.find_elements(By.XPATH, "//li[@id='contrast']")
        contrast_error = [y.find_element(By.TAG_NAME, "span").text for y in co]
        print(contrast_error)
        # alerts
        ae = driver.find_elements(By.XPATH, "//li[@id='alert']")
        alerts = [x.find_element(By.TAG_NAME, "span").text for x in ae]

        # features
        feature = driver.find_elements(By.XPATH, "//li[@id='feature']")
        features = [x.find_element(By.TAG_NAME, "span").text for x in feature]


        time.sleep(5)
        pn = driver.find_element(By.XPATH,"//button[@id='tab-details']")
        pn.click()

        time.sleep(5)
        critical_error_detail = []
        critical_error_details = []
        lbs = driver.find_elements(By.XPATH,"//ul[@id='group_list_error']/li//label")
        for i in lbs:
            critical_error_detail.append(i.text)
            for x in critical_error_detail:
                critical_error_details.append(x)

        
        cl = list(zip(critical_error, contrast_error, alerts, features))

        stmts = []
        for b in cl:
            print("Processing....5")
            web_url = url.replace("https://wave.webaim.org/report#/", "")
 
            report_link = url
            title = title.replace("WAVE Report of ", "")
            critical_error = b[0]
            contrast_error = b[1]
            alerts = b[2]
            features = b[3]
            critical_error_details = set(critical_error_details)
            critical_error_details = list(critical_error_details)
            created_at = date.today().isoformat()
            # print(critical_error_details)
            mqry = """
                INSERT INTO scrapping_data(fileName,web_url,report_link,title,critical_error,contrast_error,alerts,features,created_at,critical_error_details) 
                            VALUES  ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")
                """.format(
                file_name,
                web_url,
                report_link,
                title,
                critical_error,
                contrast_error,
                alerts,
                features,
                created_at,
                critical_error_details,
            )

            stmts.append(mqry)
            # cursor = conn.cursor()
            # here all html tag elements are inserted seprately
            # cursor.execute(mqry)
            # conn.commit()
            # print('Processing....7')

        driver.close()
        print("completed...." + url)

        return stmts
    except NoSuchElementException:
        print("url mismatch..." + url)


def runUrl(url, file_name, wait_time):
    # rsql = "SELECT web_urls FROM web_url"
    # cursor = conn.cursor()
    # cursor.execute(rsql)
    # myresult = cursor.fetchall()

    # for url in myresult:
    # print("ramesh")
    url = "https://wave.webaim.org/report#/" + url
    sql_stmts = scrapy(url, file_name, wait_time)

    return sql_stmts


if __name__ == "__main__":

    runUrl()
