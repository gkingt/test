import requests
from bs4 import BeautifulSoup
import json
import time

# 请替换以下字符串为您的实际信息
TELEGRAM_BOT_TOKEN = '6649099858:AAEplSLiDXbTkPK88kpUcrBFMK-rsQEqSZE'
CHAT_ID = '6475893897'
URL = "https://shop.aifree.best"


def fetch_data():
    """获取网页内容并提取所需数据"""
    try:
        response = requests.get(URL)
        print(f"请求网页 {URL}，响应状态码：{response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            groups = soup.findAll("div", id="group-all")
            items = groups[0].findAll("div", class_="col")
            data = [{"title": item.find("h6", class_="card-title text-truncate").text.strip(),
                     "link": item.find("a", class_="btn btn-primary fr")['href'],
                    "stock": item.find("h6", class_="mt-2").text.strip(),
                    "price": item.find("strong").text.strip(),} for item in items]
            return data
        else:
            print("网页请求失败，检查URL是否正确，或网站是否可达。")
            return []
    except Exception as e:
        print(f"获取网页数据时出错：{e}")
        return []

def save_data(data):
    """将数据保存到JSON文件"""
    with open("data.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    """从JSON文件加载数据，如果文件为空或不存在，返回空列表"""
    try:
        with open("data.json") as f:
            # 检查文件是否为空
            if f.tell() == 0 and len(f.read()) == 0:
                return []
            # 如果文件不为空，回到文件开始
            f.seek(0)
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # 如果文件不为空，但内容不是有效的JSON格式
        return []

def send_message(text):
    """发送消息到Telegram"""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage" # 使用Markdown格式化验证码
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        print(f"Telegram response: {response.text}")  # 打印Telegram API响应
    except Exception as e:
        print(f"An error occurred while sending the message to Telegram: {e}")


def find_new_items(old_data, new_data):
    """找出新的或有变化的商品信息"""
    # 使用商品链接作为唯一标识符来识别商品
    old_links = {(item['link'],item['stock'],item["price"]) for item in old_data}
    new_items = [item for item in new_data if (item['link'],item['stock'],item["price"]) not in old_links]
    return new_items

def check_for_updates():
    """检查网页是否有商品更新，并仅发送新增或变化的商品信息"""
    try:
        old_data = load_data()
        new_data = fetch_data()

        # 找出新增或变化的商品
        new_items = find_new_items(old_data, new_data)
        if new_items:
            print("发现新的或更新的商品信息，正在更新...")
            save_data(new_data)  # 更新保存的数据为最新的完整列表
            send_update_message(new_items)  # 只发送新增或变化的商品信息
        else:
            print("没有发现商品信息更新。")
    except Exception as e:
        print(f"检查更新时出错：{e}")

def send_update_message(new_items):
    """发送更新通知到Telegram，仅包括新的或变化的商品"""
    if not new_items:
        return  # 如果没有新商品，不发送消息
    messages = [f"{item['title']}: {item['link']} {item['stock']} price: {item['price']}" for item in new_items]
    message_text = "商品更新通知:\n\n" + "\n\n".join(messages)
    send_message(message_text)


# 在脚本启动时发送一条消息
send_message("Telegram Bot启动成功，现在开始监控网页内容更新。2222")

# 设置定时检查
while True:
    check_for_updates()
    time.sleep(60)  # 每分钟检查一次
