import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List

# 在下方填入你的 OpenWeather API 金鑰
WEATHER_API_KEY = 'YOUR_OPENWEATHER_API_KEY'
# 設定欲查詢的城市
CITY = 'Taipei'

# 在下方填入你的 NewsAPI 金鑰
NEWS_API_KEY = 'YOUR_NEWSAPI_KEY'
# 欲取得的新聞數量(每個分類)
NEWS_COUNT = 3
# 要抓取的新聞分類
NEWS_CATEGORIES = ['business', 'technology', 'general']


def fetch_weather(api_key: str, city: str) -> dict:
    """向 OpenWeather 取得天氣資訊"""
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',  # 取得攝氏溫度
        'lang': 'zh_tw'
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_news(api_key: str, count: int, category: str) -> List[dict]:
    """向 NewsAPI 取得指定分類的新聞標題"""
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'tw',
        'category': category,
        'pageSize': count,
        'apiKey': api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get('articles', [])


def generate_report(weather: Dict, news_by_category: Dict[str, List[dict]]) -> str:
    """整合天氣與新聞資訊為報表"""
    date_str = datetime.now(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M')
    high = weather.get('main', {}).get('temp_max')
    low = weather.get('main', {}).get('temp_min')
    description = weather.get('weather', [{}])[0].get('description')

    lines = [f'早晨匯報 - {date_str}', '-' * 20]
    lines.append(f"{CITY} 今日天氣：{description}")
    lines.append(f"最高溫 {high}°C / 最低溫 {low}°C")
    if description and '雨' in description:
        lines.append('提醒：今天可能會下雨，記得帶傘。')
    lines.append('')
    lines.append('今日新聞：')
    for cat, articles in news_by_category.items():
        lines.append(f'[{cat}]')
        for article in articles:
            title = article.get('title')
            source = article.get('source', {}).get('name')
            if title:
                if source:
                    lines.append(f"- {title} ({source})")
                else:
                    lines.append(f"- {title}")
        lines.append('')
    return '\n'.join(lines).strip()


def main():
    try:
        weather = fetch_weather(WEATHER_API_KEY, CITY)
    except Exception as e:
        print('取得天氣資訊時發生錯誤:', e)
        weather = {}

    news_by_category = {}
    for cat in NEWS_CATEGORIES:
        try:
            news_by_category[cat] = fetch_news(NEWS_API_KEY, NEWS_COUNT, cat)
        except Exception as e:
            print(f'取得{cat}新聞資訊時發生錯誤:', e)
            news_by_category[cat] = []

    report = generate_report(weather, news_by_category)
    print(report)
    with open('morning_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()
