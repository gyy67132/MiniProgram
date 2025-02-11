import requests
import json

import schedule
import time
from datetime import datetime

from ProcessingNews import generate_article
from ConcatenateWXML import generate_wxml

API_ID = "wx01e89269c07b0cae"
API_SECRET = "9f3667b7997c184e94a0e0057cfa0793"

ACCESS_TOKEN = None

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={API_ID}&secret={API_SECRET}"
    response = requests.get(url)
    data = response.json()
    #print(data)
    return data['access_token'] if 'access_token' in data else None

def add_draft(title, content, thumb_media_id, image_info, image_media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={ACCESS_TOKEN}"
    articles = {
        #必须内容
        "articles":[{
            "article_type":"news",
            "title": title,                     #标题
            "content": content,                 #图文消息的具体内容              
            "thumb_media_id": thumb_media_id   #图文消息的封面图片素材id（必须是永久MediaID）
            #"image_info": image_info,           #图片消息里的图片相关信息，图片数量最多为20张，首张图片即为封面图
            #"image_media_id": image_media_id    #图片消息里的图片素材id（必须是永久MediaID）
        }]
    }
    headers = {'Content-Type': 'application/json'}
    json_str = json.dumps(articles, ensure_ascii=False).encode('utf-8')
    response = requests.post(url, headers=headers, data=json_str)
    data = response.json()
    #print(data)
    return data['media_id'] if 'media_id' in data else None

def publish_article(media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={ACCESS_TOKEN}"
    data = {
        "media_id": media_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def send_all(media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={ACCESS_TOKEN}"
    
    data = {
        "filter":{
            "is_to_all":True,
            #"tag_id":2
            },
        "mpnews":{
            "media_id":media_id
        },
        "msgtype":"text",
        "send_ignore_reprint":0
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def batchget_material(type, offset, count):
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={ACCESS_TOKEN}"
    
    data = {
        "type":type,
        "offset":offset,
        "count":count
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def get_media_id(index):
    result = batchget_material('image', 0, 2)
    print(result)
    
    if 'item' in result and len(result['item']) > index:
        nth_media_id = result['item'][index]['media_id']
        return nth_media_id
        #print(f"第{index + 1}个media_id:", nth_media_id)
    else:
        print("获取失败或索引超出范围")

def job():
    global ACCESS_TOKEN
    print("Job Begin")
    ACCESS_TOKEN = get_access_token()
    if not ACCESS_TOKEN:
        print("获取access_token失败")
        exit()
    
    today = datetime.today().date()
    year = today.year
    month = today.month
    day = today.day

    title = f'{year}年{month}月{day}日新闻3分钟'
    #author = 'GGY'
    #content = '李自成攻下北京后，并没有意识到，当前的主要敌人，已经从明王朝变成了当时还在关外的清军。有两点可以表明，一是驻军问题，有不少大顺主力军队还安排在陕西、河南一带，用于对抗防范明军。二是对待吴三桂的态度。正是没有这样的认识，所以对待吴三桂的处理出现了问题，大顺军打吴三桂没有问题，但如果吴联合清，则情况则完全相反。山海关战役后，李自成战败，清军入关，大顺军节节败退。后期吴三桂为满清攻城拔寨，逐鹿中原，可谓立下汗马功劳。正负间，兴亡或已定。'
    news_data = generate_article()
    content = generate_wxml(news_data) 
    if not content:
        print("内容生成失败")
        exit()
    content_source_url = ''

    image_media_id = get_media_id(0)
    if not image_media_id:
        print("获取image_media_id失败")
        exit()
    
    draft_media_id = add_draft(title, content, image_media_id, "", "")
    if not draft_media_id:
        print("add draft 失败")
        exit()
    
    data = publish_article(draft_media_id)
    print("Job OK")

    # if access_token:
    #     result = upload_article(access_token, title, author, content, content_source_url)
    #     print(result)
    # else:
    #     print("获取access_token失败")
if __name__ == "__main__":
    # 每天10点运行一次
    # schedule.every().day.at("22:02").do(job)
    
    # print("定时任务已启动，等待执行...")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    job()

    

