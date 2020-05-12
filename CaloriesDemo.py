from gevent import monkey

monkey.patch_all()

import gevent, requests, bs4, openpyxl
from gevent.queue import Queue

work = Queue()

url_1 = "http://www.boohee.com/food/group/{type}?page={page}"
for i in range(1, 4):
    for j in range(1, 4):
        real_url = url_1.format(type=i, page=j)
        work.put_nowait(real_url)

url_2 = "http://www.boohee.com/food/view_menu?page={page}"
for x in range(1, 4):
    real_url = url_2.format(page=x)
    work.put_nowait(real_url)


def crawler():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    while not work.empty():
        url = work.get_nowait()
        res = requests.get(url, headers=headers)
        bs_res = bs4.BeautifulSoup(res.text, "html.parser")
        foods = bs_res.find_all("li", class_="item clearfix")
        for food in foods:
            food_name = food.find_all("a")[1]["title"]
            food_url = "http://www.boohee.com" + food.find_all("a")[1]["href"]
            food_calorie = food.find("p").text
            sheet.append([food_name, food_calorie, food_url])


tasks_list = []
# 创建空的任务列表

wb = openpyxl.Workbook()
sheet = wb.active
sheet["A1"] = "食物"
sheet["B1"] = "热量"
sheet["C1"] = "链接"


for x in range(5):
    # 相当于创建了5个爬虫
    task = gevent.spawn(crawler)
    # 用gevent.spawn()函数创建执行crawler()函数的任务。
    tasks_list.append(task)
    # 往任务列表添加任务。
gevent.joinall(tasks_list)

wb.save("Calories.xlsx")
# 用gevent.joinall方法，启动协程，执行任务列表里的所有任务，让爬虫开始爬取网站。
