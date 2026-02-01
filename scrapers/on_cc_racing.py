import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def scrape():
    # 重點：這個網址才是選單真正所在的頁面
    target_url = "https://racing.on.cc/racing/new/lastwin/index.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://racing.on.cc/news.html'
    }
    
    print(f"正在存取東方馬經選單...")
    
    try:
        res = requests.get(target_url, headers=headers)
        # 強制指定編碼為 Big5 (cp950)，防止中文亂碼
        res.encoding = 'cp950' 
        
        if res.status_code != 200:
            print(f"東方馬經存取失敗: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 尋找 class 為 rac_news_selection 的 select 標籤
        news_select = soup.find('select', class_='rac_news_selection')
        if not news_select:
            print("找不到新聞選單標籤 (rac_news_selection)")
            return []

        options = news_select.find_all('option')
        extracted_data = []
        seen_titles = set()

        # 設定過濾日期 (抓今天 20260201)
        target_date = datetime.now().strftime("%Y%m%d")
        print(f"尋找日期為 {target_date} 的新聞...")

        for opt in options:
            val = opt.get('value', '')
            title = opt.get_text(strip=True)
            
            # 東方的 value 格式通常是 bknrac-202602011437-0129_01002_001
            if target_date in val:
                if title and "請選擇" not in title and title not in seen_titles:
                    seen_titles.add(title)
                    extracted_data.append({
                        "title": f"[東方] {title}",
                        "link": "https://racing.on.cc/news.html",
                        "time": datetime.now().strftime("%Y-%m-%d")
                    })
        
        print(f"東方馬經成功抓取 {len(extracted_data)} 則標題")
        return extracted_data

    except Exception as e:
        print(f"東方馬經執行出錯: {e}")
        return []
