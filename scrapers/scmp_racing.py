import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def parse_scmp_date(date_str):
    if not date_str: return None
    try:
        # 格式範例: 1 Feb 2026 - 7:30 AM
        # 移除 "Updated:" 等字眼並只取第一行
        clean_date = date_str.strip().replace('Updated: ', '').split('\n')[0]
        return datetime.strptime(clean_date, "%d %b %Y - %I:%M %p")
    except Exception:
        return None

def scrape():
    base_url = "https://www.scmp.com"
    news_url = "https://www.scmp.com/sport/racing/news"
    
    # 強化 Headers，模擬真實 Mac 瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,arm64e/v1,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    
    print(f"--- 啟動 SCMP 抓取 ---")
    res = requests.get(news_url, headers=headers)
    if res.status_code != 200:
        print(f"SCMP 存取失敗，狀態碼: {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    extracted_data = []
    seen_links = set()
    
    # 設定時間門檻 (測試 48 小時)
    threshold = datetime.now() - timedelta(hours=48)

    # 策略：尋找頁面上所有包含 "/sport/racing/" 的新聞連結
    # SCMP 的新聞網址通常包含 "/sport/racing/article/"
    all_links = soup.find_all('a', href=re.compile(r'/sport/racing/article/'))
    print(f"找到 {len(all_links)} 個馬經新聞連結標籤，開始解析...")

    for a in all_links:
        link = a.get('href', '')
        full_link = base_url + link if link.startswith('/') else link
        
        # 避免重複抓取同一個連結
        if full_link in seen_links:
            continue
            
        # 取得標題
        title = a.get_text(strip=True)
        # 如果 a 標籤裡面沒字（可能是圖片），去旁邊找找看有沒有標題標籤
        if len(title) < 5:
            parent = a.find_parent(['div', 'article'])
            if parent:
                title_node = parent.find(['h1', 'h2', 'h3'])
                if title_node:
                    title = title_node.get_text(strip=True)

        # 如果還是沒標題，就跳過
        if len(title) < 5:
            continue

        # 關鍵：尋找時間戳記
        # 我們在連結所在的「區塊容器」內尋找任何包含 timestamp 字眼的標籤
        container = a.find_parent(['div', 'article', 'section'])
        time_tag = None
        if container:
            time_tag = container.select_one('[class*="timestamp"]')
        
        # 如果容器內沒找到，試著找該標籤附近的 span
        if not time_tag and container:
            time_tag = container.find_next('span', class_=re.compile(r'timestamp'))

        if time_tag:
            raw_time = time_tag.get_text(strip=True)
            pub_date = parse_scmp_date(raw_time)
            
            if pub_date and pub_date >= threshold:
                seen_links.add(full_link)
                extracted_data.append({
                    "title": title,
                    "link": full_link,
                    "time": pub_date.strftime("%Y-%m-%d %H:%M")
                })
                print(f"成功: {title[:25]}... [{raw_time}]")

    # 根據時間排序 (最新在前面)
    extracted_data.sort(key=lambda x: x['time'], reverse=True)
    
    if not extracted_data:
        print("警告：解析完畢但沒有符合 48 小時內的文章。")
        
    return extracted_data
