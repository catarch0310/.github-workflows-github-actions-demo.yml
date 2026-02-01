import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def parse_scmp_date(date_str):
    """
    將 SCMP 的日期字串 (例如: '1 Feb 2026 - 7:30 AM' 或 '31 Jan 2026 - 4:53 PM') 
    轉換為 datetime 物件
    """
    try:
        # 去除多餘空白並解析格式
        # 格式範例: 31 Jan 2026 - 4:53 PM
        clean_date = date_str.strip()
        return datetime.strptime(clean_date, "%d %b %Y - %I:%M %p")
    except Exception as e:
        print(f"日期解析失敗: {date_str}, 錯誤: {e}")
        return None

def scrape():
    base_url = "https://www.scmp.com"
    news_url = "https://www.scmp.com/sport/racing/news"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    res = requests.get(news_url, headers=headers)
    if res.status_code != 200:
        print(f"SCMP 存取失敗: {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    extracted_data = []
    
    # 定義 48 小時前的時間點
    now = datetime.now()
    threshold = now - timedelta(hours=500)

    # 1. 抓取大頭條 (h1)
    # 根據截圖，大頭條在 h1.news-content-title 內
    main_article = soup.select_one('h1.news-content-title')
    if main_article:
        a_tag = main_article.find('a')
        # 尋找對應的時間戳記
        time_tag = soup.select_one('.article-lv1__timestamp')
        
        if a_tag and time_tag:
            title = a_tag.get_text(strip=True)
            link = base_url + a_tag.get('href', '')
            pub_date = parse_scmp_date(time_tag.get_text(strip=True))
            
            if pub_date and pub_date >= threshold:
                extracted_data.append({
                    "title": f"[Top] {title}",
                    "link": link,
                    "time": pub_date.strftime("%Y-%m-%d %H:%M")
                })

    # 2. 抓取次要新聞 (h3)
    # 根據截圖，這些在 article.article-lv3 標籤內
    sub_articles = soup.select('article.article-lv3')
    for art in sub_articles:
        title_tag = art.select_one('h3 a')
        time_tag = art.select_one('.article-lv3__timestamp')
        
        if title_tag and time_tag:
            title = title_tag.get_text(strip=True)
            link = base_url + title_tag.get('href', '')
            pub_date = parse_scmp_date(time_tag.get_text(strip=True))
            
            # 過濾 48 小時內的內容
            if pub_date and pub_date >= threshold:
                extracted_data.append({
                    "title": title,
                    "link": link,
                    "time": pub_date.strftime("%Y-%m-%d %H:%M")
                })

    return extracted_data
