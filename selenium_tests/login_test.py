from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.maximize_window()

driver.get("http://127.0.0.1:8000/")

driver.find_element(By.NAME, "username").send_keys("omcsit22@oic.edu.np")

driver.find_element(By.NAME, "password").send_keys("utsab@12")

driver.find_element(By.TAG_NAME, "button").click()
time.sleep(3)

print(driver.title)

print("Closing browser...")

driver.quit()

print("Browser closed.")