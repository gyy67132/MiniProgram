import requests
import json
import time

from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from GetNews import get_news_list
from GetNews import NEWS_NUM

API_KEY = "sk-0a5ee8f64c784c8d8de424aebb0061d3"
API_URL = "https://api.deepseek.com/v1/chat/completions"

def choose_news(news_list, num):
    news_list_string = ""
    for index, item in enumerate(news_list):
        if(index != len(news_list) - 1):
            news_list_string += f"{item}|"
        else:
            news_list_string += f"{item}"
    
    total_news_num = len(news_list)

    try:
        
        prompt = f"""处理输入的新闻字符串，字符串由多条新闻组成，新闻总数为{total_news_num}条，每条新闻内容之间以|分隔，输出{num}条新闻内容组成的字符串，仍以'|'分隔。

多个新闻内容字符串：{news_list_string}

要求：
1. 请将输入的多个新闻内容进行删除，保留{num}条新闻内容。
2. 删除内容错误无效的新闻，删除内容相近的新闻，删除过长或者过短的新闻。
3. 输出也是字符串，字符串由{num}条新闻内容组成，每条新闻内容之间以|分隔。
4. 输出内容只包含新闻内容，不包含任何其他内容，字符串头尾的'符号请删除"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # 使用带有重试机制的 session
        session = create_requests_session()
        
        # 增加超时时间
        response = session.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=(30, 90)  # (连接超时, 读取超时)
        )

        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            print(text)
            return_news_list = text.split('|')
            if(len(return_news_list) != num):
                print(f"新闻数量不匹配，返回数量：{len(return_news_list)}，要求数量：{num}")
                return None
            return text.split('|')
        else:
            print(f"API请求失败，状态码：{response.status_code}")
            print(f"错误信息：{response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"处理超时...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
        return None
    except Exception as e:
        print(f"处理新闻时出错: {str(e)}")
        return None
    finally:
        session.close()

def create_requests_session():
    """创建一个带有重试机制的 session"""
    session = requests.Session()
    
    # 配置重试策略
    retries = Retry(
        total=3,  # 总重试次数
        backoff_factor=1,  # 重试间隔时间
        status_forcelist=[500, 502, 503, 504, 429],  # 需要重试的HTTP状态码
    )
    
    # 配置 session
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session
    
def process_single_news(content):
    try:
        # 限制输入内容长度
        content = content[:2000] if content else ""
        
        prompt = f"""请将输入的新闻内容进行概括和缩略，输出内容缩略。

新闻内容：{content}

要求：
1. 内容缩略要求对新闻内容进行概括整理，输出字数在30-100字左右，保留关键信息。个别新闻内容长的，内容缩略可以保留100-200字左右。
2. 输出格式是字符串，类似这样:'曾隐姓埋名30年，中国第一代核潜艇工程总设计师黄旭华院士，于2月6日在湖北武汉逝世，享年99岁。'
3. 新闻内容不要出现某某某拍摄，某某某撰稿等新闻编辑相关的内容，请删除这些内容
4. 图片信息也删除，不要有图片相关的信息"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # 使用带有重试机制的 session
        session = create_requests_session()
        
        # 增加超时时间
        response = session.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=(30, 90)  # (连接超时, 读取超时)
        )

        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            print(text)
            return text
        else:
            print(f"API请求失败，状态码：{response.status_code}")
            print(f"错误信息：{response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"处理超时...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {str(e)}")
        return None
    except Exception as e:
        print(f"处理新闻时出错: {str(e)}")
        return None
    finally:
        session.close()

def process_news_list(test_news):
    processed_news = []
    total = len(test_news)
    
    for index, content in enumerate(test_news):
        print(f"处理第 {index}/{total} 条新闻...")
        
        time_flag = 0
        while True:
            try:
                result = process_single_news(content)
                if result:
                    processed_news.append(result)                    
                    break  # 成功处理，跳出重试循环
                else:
                    time_flag += 1

            except Exception as e:
                time_flag += 1        
        # 在每次请求之间添加延时
        time.sleep(1 + time_flag * 3)
    
    return processed_news

def generate_article():
    test_news = get_news_list()
    if test_news is None:
        print("新闻获取失败")
        return None

    result_news = []
    return_news = []
    
    for group_index,news_group in enumerate(test_news):
        news_list = process_news_list(news_group)
        result_news.append(news_list)

    for index, item in enumerate(result_news):
       news_list = choose_news(item, NEWS_NUM[index])
       return_news.append(news_list)

    return return_news

# from openai import OpenAI

# client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False
# )
# print(response.choices[0].message.content)
