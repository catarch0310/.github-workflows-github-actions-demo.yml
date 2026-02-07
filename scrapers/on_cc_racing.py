import requests
import re
from datetime import datetime, timedelta

def scrape():
    # 這是東方馬經兩個最穩定的數據入口
    urls = [
        "https://racing.on.cc/racing/new/news_content.html",
        "https://racing.on.cc/racing/new/lastwin/index.html",
        "https://racing.on.cc/news.html"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://racing.on.cc/'
    }
    
    extracted_data = []
    seen_titles = set()
    
    # 取得日期標籤 (例如 1/2)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    target_dates = [f"{now.day}/{now.month}", f"{yesterday.day}/{yesterday.month}"]
    
    print(f"--- 啟動東方馬經超級暴力掃描 (目標日期: {target_dates}) ---")

    for url in urls:
        try:
            print(f"正在全文本掃描: {url}")
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = 'cp950' # 確保中文編碼
            
            if res.status_code != 200:
                continue

            # --- 大絕招：正規表達式 ---
            # 直接尋找網頁原始碼中所有 <option> 標籤內的文字
            # 不管它在哪個層級，通通挖出來
            raw_matches = re.findall(r'<option[^>]*>(.*?)</option>', res.text)
            
            if raw_matches:
                print(f"  ✅ 發現 {len(raw_matches)} 個可能的選項...")
                
                for title in raw_matches:
                    title = title.strip()
                    # 排除掉無意義的短字或提示語
                    if len(title) > 6 and "請選擇" not in title:
                        if title not in seen_titles:
                            # 如果標題裡面有 [戰況] 或是長得像新聞，就收
                            # 我們稍微放寬條件，不強求日期標籤，因為標題通常已經包含日期特徵
                            seen_titles.add(title)
                            extracted_data.append({
                                "title": f"[東方] {title}",
                                "link": "https://racing.on.cc/news.html",
                                "time": datetime.now().strftime("%Y-%m-%d")
                            })
                
                if extracted_data:
                    print(f"  ✨ 成功！從原始碼直接挖出 {len(extracted_data)} 則新聞")
                    break

        except Exception as e:
            print(f"  ❌ 掃描失敗: {e}")

    return extracted_data
