import pandas as pd
from datetime import datetime
import os
import importlib

# 這裡列出所有 scrapers 資料夾下的模組名
SCRAPER_SITES = [
    'racing_post',
    'scmp_racing',
    'at_the_races',
    # 之後新增網站只要在這裡加名字即可
]

def run_all():
    all_headlines = []
    
    for site in SCRAPER_SITES:
        try:
            print(f"--- 正在執行 {site} 爬蟲 ---")
            # 動態載入模組
            module = importlib.import_module(f"scrapers.{site}")
            data = module.scrape() # 規定每個模組都要有一個 scrape() 函式
            
            if data:
                # 加入來源標記
                for item in data:
                    item['source'] = site
                all_headlines.extend(data)
                print(f"成功抓取 {site}，共 {len(data)} 則")
            
        except Exception as e:
            print(f"錯誤: {site} 執行失敗: {e}")

    if all_headlines:
        df = pd.DataFrame(all_headlines)
        os.makedirs('data', exist_ok=True)
        filename = f"data/all_racing_news_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n任務完成！所有資料已存至 {filename}")

if __name__ == "__main__":
    run_all()
