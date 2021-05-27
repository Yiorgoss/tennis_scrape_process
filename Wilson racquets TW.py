from bs4 import BeautifulSoup as soup 
from urllib.request import urlopen as uReq  
import requests
import os.path

page_url = "https://www.tenniswarehouse-europe.com/catpage-WILSONRACS-EN.html"

save_path = 'C:\\Users\\Lefteris\\OneDrive\\Desktop\\Scrape Excels'


response = requests.get(page_url, cookies={'SMID':'smc_fbIdmC7VmLvxzHBD0pXTqbYo7kSYh69hqcKQ02xE_239306669'})
soup = soup(response.text, 'html.parser')



containers = soup.findAll("div", {"class":"product_wrapper cf rac"})


filename = "WilsonRacquets"
completeName = os.path.join(save_path, filename+".csv")
f = open(completeName, 'w')

headers = "Name, Price\n"

f.write(headers)

for container in containers:
    name = container.div.img["alt"]
    price = container.span.span.text
    #print("Name: " + name +  "\n" + "Price: " + price + "\n")
    f.write(name.replace("Wilson ", "") + "," + price.replace(",", ".") + '\n')
    