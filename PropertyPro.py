# Importing Libraries
from bs4 import BeautifulSoup
import requests, re, time, pandas as pd 
from urllib.parse import urljoin
from urllib import robotparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#SCRAPPING DATA FROM PROPERTYPRO.NG

# Checking if I am allowed to Scrape this site
robots = robotparser.RobotFileParser()
robots.set_url("https://www.propertypro.ng/robots.txt")
robots.read()

target_path = "/property-for-rent/in/lagos"
is_allowed = robots.can_fetch("*", f"https://www.propertypro.ng{target_path}")
print("Allowed to scrape this path:", is_allowed)


# Setting up chrome to access the property website
chrome_opts = Options()
chrome_opts.add_argument("--headless=new")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--no-sandbox")
chrome_opts.add_argument("--window-size=1366,768")
chrome_opts.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

service = Service(r"C:\Users\user\OneDrive\Documents\Lagos Housing Data\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_opts)

#Scrapping Data from multiple pages, storing them into vectors and joining them
#in a dataframe
site_url = "https://www.propertypro.ng/property-for-rent/in/lagos?page="

records = []

def parse_price(text):
    match = re.search(r"₦\s*([\d,]+)", text or "")
    return int(match.group(1).replace(",", "")) if match else None


for page_no in range(451, 499):   # TEST with 1–4 first; later change to (1, 803)
    url = f"{site_url}{page_no}"
    driver.get(url) 
    time.sleep(3)

soup = BeautifulSoup(driver.page_source, "lxml")

cards = soup.find_all("div", class_="property-listing")
if not cards:
        cards = soup.find_all("div", class_="single-room-text")  


if page_no % 25 == 0: 
    driver.quit() 
    time.sleep(5) 
    driver = webdriver.Chrome(service=service, options=chrome_opts)

for card in cards:
        # description
        desc_tag = card.select_one("div.pl-title a")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        # location
        loc_tag = card.select_one("div.pl-title p")
        location = loc_tag.get_text(strip=True) if loc_tag else None

        # price
        price_tag = card.select_one("div.pl-price")
        price_raw = price_tag.get_text(strip=True) if price_tag else None
        price = parse_price(price_raw)  

        # extract bed/bath counts using regex
        text = card.get_text(" ", strip=True).lower()
        def pick(rx):
            m = re.search(rx, text)
            return int(m.group(1)) if m else None

        beds = pick(r"(\d+)\s*bed")
        baths = pick(r"(\d+)\s*bath")

        records.append({
            "description": description,
            "location": location,
            "price_naira": price,
            "bedrooms": beds,
            "bathrooms": baths,
        })

        print(f"Scraped page {page_no}, got {len(cards)} listings")

# ========== CLEANUP ==========
driver.quit()

# ========== DATAFRAME ==========
df = pd.DataFrame(records)
print(df.head())

# Save to CSV
df.to_csv("lagos_pg451_498.csv", index=False, encoding="utf-8")
print("Saved lagos_pg451_498.csv with", len(df), "rows")

    
