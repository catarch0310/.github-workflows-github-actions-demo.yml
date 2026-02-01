import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

def scrape_racing_post():
    base_url = "https://www.racingpost.com"
    news_url = "https://www.racingpost.com/news/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,arm64e/v1,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }
    
    print(f"正在存取: {news_url}")
    session = requests.Session()
    response = session.get(news_url, headers=headers)
    
    if response.status_code != 200:
        print(f"無法存取，錯誤代碼: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 根據截圖，目標在 data-testid 包含 "Link__" 且結尾是 "__Article" 的 a 標籤
    # 我們抓取所有符合這條規則的連結
    article_tags = soup.find_all('a', attrs={'data-testid': lambda x: x and x.startswith('Link__') and x.endswith('__Article')})
    
    news_list = []
    seen_links = set()

    for tag in article_tags:
        link = tag.get('href')
        if not link: continue
        
        full_link = base_url + link if link.startswith('/') else link
        
        # 避免重複抓取相同的連結
        if full_link in seen_links: continue
        seen_links.add(full_link)
        
        # 標題通常就在標籤的文字裡，或是裡面的 <span> 標籤
        title = tag.get_text(strip=True)
        if not title: continue

        news_list.append({
            "title": title,
            "link": full_link
        })

    print(f"找到 {len(news_list)} 則新聞，開始抓取內文...")

    # 抓取前 5 則的全文
    results = []
    for item in news_list[:5]:
        try:
            print(f"抓取內文: {item['title']}")
            res = session.get(item['link'], headers=headers)
            detail_soup = BeautifulSoup(res.text, 'html.parser')
            
            # 針對 Racing Post 內文，通常在 <p> 標籤中
            # 排除掉無意義的短句
            paragraphs = detail_soup.find_all('p')
            full_text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 40])
            
            results.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": item['title'],
                "link": item['link'],
                "content": full_text
            })
            time.sleep(2) # 禮貌抓取
        except Exception as e:
            print(f"錯誤連結 {item['link']}: {e}")

    if results:
        df = pd.DataFrame(results)
        os.makedirs('data', exist_ok=True)
        filename = f"data/racing_post_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"成功儲存: {filename}")

if __name__ == "__main__":
    scrape_racing_post()
