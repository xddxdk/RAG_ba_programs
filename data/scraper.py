from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

base_url = "https://tsu.ru/"
catalog_url = "https://tsu.ru/ba"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver

def get_program_links(driver):
    """Получает ссылки на все образовательные программы"""
    driver.get(catalog_url)
    time.sleep(2)
    
    programs = driver.find_elements(By.CLASS_NAME, "link")
    links = []
    # убираем лишние ссылки и пустые значения
    for tag in programs:
        href = tag.get_attribute("href")
        if href and href.startswith("https://www.tsu.ru/ba/"):
            links.append(href.rstrip('/'))
    return list(set(links))
    
def get_program_info(driver, url):
    """Получает название и описание программ"""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "h1")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None
    # Поиск названий
    try:
        title = soup.find("h1").text.strip()
    except:
        title = "Нет названия"
    # Поиск описаний
    try:
        header_div = soup.find("div", class_="with-indent lead-in _builder builder--text")
        description = header_div.get_text(separator=" ", strip=True) if header_div else "Нет описания"
    except:
        description = "Нет описания"
    return {
        "title": title,
        "description": description,
        "url": url
    }
    
def main():
    driver = get_driver()
    try:
        links = get_program_links(driver)
        data = []
        for link in tqdm(links, desc="Парсинг программ обучения"):
            try:
                info = get_program_info(driver, link)
                data.append(info)
            except Exception as e:
                print(f"Ошибка при обработке {link}: {e}")
        df = pd.DataFrame(data)
        df.to_csv("programs.csv", index=False)
    finally:
        driver.quit()
        
if __name__ == "__main__":
    main()