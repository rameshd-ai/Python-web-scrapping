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


def scrapy(url, file_name):
    try:
        print("Generating no of pages....1")
        time.sleep(30)
        print("Generating no of pages....2")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # driver.implicitly_wait(10)
        driver.get(url)
        time.sleep(30)
        print("Generating no of pages....3")
        # title
        title = driver.title
        # critical_error
        ce = driver.find_elements(By.XPATH, "//li[@id='error']")
        critical_error = [x.find_element(By.TAG_NAME, "span").text for x in ce]

        # contrast_error
        ce = driver.find_elements(By.XPATH, "//li[@id='contrast']")
        contrast_error = [x.find_element(By.TAG_NAME, "span").text for x in ce]

        # alerts
        ae = driver.find_elements(By.XPATH, "//li[@id='alert']")
        alerts = [x.find_element(By.TAG_NAME, "span").text for x in ae]

        # features
        feature = driver.find_elements(By.XPATH, "//li[@id='feature']")
        features = [x.find_element(By.TAG_NAME, "span").text for x in feature]

        cl = list(zip(critical_error, contrast_error, alerts, features))
        for b in cl:
            print("Processing....5")
            web_url = url.replace("https://wave.webaim.org/report#/", "")
            report_link = url
            title = title.replace("WAVE Report of ", "")
            critical_error = b[0]
            contrast_error = b[1]
            alerts = b[2]
            features = b[3]
            created_at = date.today().isoformat()
            mqry = """
                INSERT INTO scrapping_data(fileName,web_url,report_link,title,critical_error,contrast_error,alerts,features,created_at) 
                            VALUES  ("{}","{}","{}","{}","{}","{}","{}","{}","{}")
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
            )

            return mqry
            # cursor = conn.cursor()
            # here all html tag elements are inserted seprately
            # cursor.execute(mqry)
            # conn.commit()
            # print('Processing....7')
        driver.close()
        print("completed...." + url)
    except NoSuchElementException:
        print("url mismatch..." + url)


def runUrl(url, file_name):
    # rsql = "SELECT web_urls FROM web_url"
    # cursor = conn.cursor()
    # cursor.execute(rsql)
    # myresult = cursor.fetchall()

    # for url in myresult:
    # print("ramesh")
    # url = "https://wave.webaim.org/report#/" + url
    print(url)
    sql_stmt = scrapy(url, file_name)
    time.sleep(2)
    return sql_stmt


if __name__ == "__main__":

    runUrl()
