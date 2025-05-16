import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

url = "https://genshin-info.ru/wiki/personazhi/"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(4)

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()


cards = soup.find_all('a', class_='itemcard')

data = []
char_driver=webdriver.Chrome(options=options)
flag=False
try:
    for card in cards:
        name=None
        element=None
        weapon=None
        stars=None
        
        char_link=card['href']
        print(char_link)
        char_driver.get(url.replace("/wiki/personazhi/","")+char_link)
        char_soup=BeautifulSoup(char_driver.page_source, 'html.parser')

        
        
        name = char_soup.find('div', class_='characterPromo__name').text.strip()
        print(name)
        
        cd = char_soup.find_all('div', "characterPromo__prop")
        
        element = cd[1].find('span',class_="characterPromo__propV").text.strip()# char_soup.find('span', class_='characterPromo__propV')
        
        print(element)
        
        weapon = cd[2].find('span', class_='characterPromo__propV').text.strip()
        
        print(weapon)
        
        stars = len(char_soup.find_all('i', class_="fa fa-star"))
        print(stars)
        
        
        data.append({
            "Имя": name,
            "Элемент": element,
            "Оружие": weapon,
            "Редкость": stars
        })
except:
    flag=True
    
    char_driver.quit()
    df = pd.DataFrame(data)
    df.to_csv("genshin_characters.csv", index=False)
    df.head()
if not(flag):
    char_driver.quit()
    df = pd.DataFrame(data)
    df.to_csv("genshin_characters.csv", index=False)
    df.head()
    
