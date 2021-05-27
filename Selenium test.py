from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd 
import time

df = pd.read_csv('C:\\Users\\Lefteris\\OneDrive\\Desktop\\Scripts\\Selenium\\EXCELS FOR SELENIUM\\Wilson beginners selinium test.csv')

PATH = "C:\\Program Files (x86)\\chromedriver.exe"
driver = webdriver.Chrome(PATH)

driver.get("https://www.e-tennis.com/index.php/e1mp73yt5fr0s98rmfs7rq/customer/index/key/1452c629c6f3cb7dc0465d3ba859dba2/")

#Login
driver.find_element_by_xpath('//*[@id="username"]').send_keys("monica")
driver.find_element_by_id("login").send_keys("monica123")
driver.find_element_by_class_name("form-button").click()

#Popup
driver.find_element_by_xpath("//*[@id='message-popup-window']/div[1]/a/span").click()

#Catalog > Manage Products
driver.find_element_by_xpath("//*[@id='nav']/li[2]/a/span").click()
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[3]/ul/li[2]/ul/li[1]/a").click()
 
#Select Store
driver.find_element_by_id("store_switcher").click()
driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/p/select/optgroup[10]/option[1]").click()


for _,row in df.iterrows():
	try:
		#Paste SKU
		element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="productGrid_product_filter_sku"]')))
		element.clear()
		element.send_keys(row.SKU)
	except:
		print("=========================================================")
	#submit
	driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[3]/div/table/tbody/tr/td[3]/button[2]').click()

	time.sleep(5)
	#select all
	element1 = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/div[3]/div/div[1]/table/tbody/tr/td[1]/a[1]')))
	# element1 = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[3]/div/div[1]/table/tbody/tr/td[1]/a[1]')
	element1.click()

	#update attributes
	driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[3]/div/div[1]/table/tbody/tr/td[2]/div/div[1]/form/fieldset/span[1]/select/option[4]').click()
	driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[3]/div/div[1]/table/tbody/tr/td[2]/div/div[1]/form/fieldset/span[4]/button').click()


	driver.find_element_by_xpath('//*[@id="special_price-checkbox"]').click()
	driver.find_element_by_xpath('//*[@id="special_price"]').send_keys(row[2].replace('€', '').replace('.', ','))
	driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div[2]/div/div[2]/table/tbody/tr/td[2]/button[3]').click()
	print("price changed", row.SKU, "new price =", row[2].replace('€', 'euros'))

driver.quit()

