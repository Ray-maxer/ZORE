import requests
from datetime import datetime

# 在下方填入你的 OpenWeather API 金鑰
WEATHER_API_KEY = '3be98769c7406760c052e7602de181f9'
# 設定欲查詢的城市
CITY = 'Taipei'

# 在下方填入你的 NewsAPI 金鑰
NEWS_API_KEY = '6449d0d2a33f45799b35c91cc4e976ee'
# 欲取得的新聞數量
NEWS_COUNT = 5


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


def fetch_news(api_key: str, count: int) -> list:
    """向 NewsAPI 取得新聞標題"""
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'tw',
        'pageSize': count,
        'apiKey': api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get('articles', [])


def generate_report(weather: dict, news: list) -> str:
    """整合天氣與新聞資訊為報表"""
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    high = weather.get('main', {}).get('temp_max')
    low = weather.get('main', {}).get('temp_min')
    description = weather.get('weather', [{}])[0].get('description')

    lines = [f'早晨匯報 - {date_str}', '-' * 20]
    lines.append(f"{CITY} 今日天氣：{description}")
    lines.append(f"最高溫 {high}°C / 最低溫 {low}°C")
    if 'rain' in description:
        lines.append('提醒：今天可能會下雨，記得帶傘。')
    lines.append('')
    lines.append('今日新聞：')
    for article in news:
        title = article.get('title')
        if title:
            lines.append(f"- {title}")
    return '\n'.join(lines)


def main():
    try:
        weather = fetch_weather(WEATHER_API_KEY, CITY)
    except Exception as e:
        print('取得天氣資訊時發生錯誤:', e)
        weather = {}

    try:
        news = fetch_news(NEWS_API_KEY, NEWS_COUNT)
    except Exception as e:
        print('取得新聞資訊時發生錯誤:', e)
        news = []

    report = generate_report(weather, news)
    print(report)
    with open('morning_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()
