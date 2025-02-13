import requests
import json
import os
from datetime import datetime

from ProcessingNews import generate_context
from ConcatenateWXML import generate_wxml

#API_ID = "wx01e89269c07b0cae"
#API_SECRET = "9f3667b7997c184e94a0e0057cfa0793"

API_ID = "wx1f315a96f32a2078"
API_SECRET = "d279df278b1513b8f2ea4edf1f238289"

ACCESS_TOKEN = None

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={API_ID}&secret={API_SECRET}"
    response = requests.get(url)
    data = response.json()
    #print(data)
    return data['access_token'] if 'access_token' in data else None

def get_user_openid():
    url = f"https://api.weixin.qq.com/cgi-bin/user/get?access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()['data']
    return data['openid'] if 'openid' in data else None

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

def media_upload():
    url = f'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={ACCESS_TOKEN}&type=image'
    file_path = r'E:\ggy\公众号用AI自动发布新闻\b.jpg'  # 替换成你的图片路径
    #file_path = os.path.abspath('E:\\ggy\\公众号用AI自动发布新闻\\a.jpeg')  # 使用绝对路径
    #headers = {'Content-Type': 'application/octet-stream'}  # 根据图片格式设置Content-Type

    with open(file_path, 'rb') as f:
        files = {'media': (os.path.basename(file_path), f, 'image/jpg')}
        response = requests.post(url, files=files)

    if response.status_code != 200:
        print('上传图片失败，错误码：', response.status_code)
        return None
    data = response.json()
    print(data)
    return data['media_id'] if 'media_id' in data else None

def publish_article(media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={ACCESS_TOKEN}"
    data = {
        "media_id": media_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("publish_article:")
    print(response.json())
    return response.json()

def send_all(media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={ACCESS_TOKEN}"
    
    data = {
        "filter":{
            "is_to_all":True,
            },
        "mpnews":{
            "media_id": media_id
        },
        "msgtype":"mpnews",
        "send_ignore_reprint":1
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("send_all:")
    print(response.json())
    return response.json()

def send_article(openids, mdeia_id):
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token={ACCESS_TOKEN}"
    data = {
        "touser":[
           openids
        ],
        "mpnews":{
                "media_id":mdeia_id
            },
        "msgtype":"mpnews",
        "send_ignore_reprint":0
    }
    response = requests.post(url, data=json.dumps(data, ensure_ascii=False)).json()
    print("https://api.weixin.qq.com/cgi-bin/message/mass/send\n")
    print(response)
    return response

def get_send_status():
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/get?access_token={ACCESS_TOKEN}"
    data = {
        "msg_id": "3147483652"
    }
    headers = {'Content-Type': 'application/json'}  # 添加headers
    response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False))
    print(f"get_send_status: {response.json()}")
    return response.json()

def uploadnews(title, content, media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadnews?access_token={ACCESS_TOKEN}"
    data = {
            "articles": [	 
            {
                "thumb_media_id" : media_id,
                "author":"ggy",		
                "title": title,		 
                #"content_source_url":"www.qq.com",		
                "content":content,		 
                #"digest":"digest",
                #"show_cover_pic":1,
                #"need_open_comment":1,
                #"only_fans_can_comment":1
            }]
    }
    response = requests.post(url, data=json.dumps(data, ensure_ascii=False)).json()
    print("uploadnews:")
    print(response)
    return response['media_id'] if 'media_id' in response else None

def batchget_material(type, offset, count):
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={ACCESS_TOKEN}"
    
    data = {
        "type": type,
        "offset":offset,
        "count":count
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def get_media_id(index):
    result = batchget_material('image', 0, 2)
    #print(result)
    
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
    #content = '李自成攻下北京后，并没有意识到，当前的主要敌人，已经从明王朝变成了当时还在关外的清军。有两点可以表明，一是驻军问题，有不少大顺主力军队还安排在陕西、
    news_data = generate_context()
    content = generate_wxml(news_data) 
    if not content:
        print("内容生成失败")
        exit()
    content_source_url = ''

    if True:
        image_media_id = get_media_id(0)
        if not image_media_id:
            print("获取image_media_id失败")
            exit()
        
        draft_media_id = add_draft(title, content, image_media_id, "", "")
        if not draft_media_id:
            print("add draft 失败")
            exit()
        #print( image_media_id)
        publish_article(draft_media_id)
    else:
        openid = get_user_openid()
        print(openid)
        
        image_media_id = "_NYVb43u7DknhLmwDz5pGCBPWmzy6qL15IctVQ_FYv85KzkEqDFHKY7Zv6RqsTnY"#media_upload()

        mdeia_id = uploadnews(title, content, image_media_id)
        #data = send_all(content)
        
        #send_article(openid, mdeia_id)
        send_all(mdeia_id)

    print("Job End")

    

