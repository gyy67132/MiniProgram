import requests
import json
import time

from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from GetNews import get_news_list
from GetNews import NEWS_NUM,NEWS_TYPE

API_KEY = "sk-kienwrrlpkscoeydqofzfgjmewvmdmmfzadavuoupqpyeosx"
#"sk-0a5ee8f64c784c8d8de424aebb0061d3"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
#"https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"
#MODEL_NAME = "deepseek-chat"


def choose_news(news_list, num):
    news_list_string = ""
    for index, item in enumerate(news_list):
        if(index != len(news_list) - 1):
            news_list_string += f"{item}|"
        else:
            news_list_string += f"{item}"
    
    total_news_num = len(news_list)

    try:
        
        prompt = f"""处理输入的新闻字符串，字符串由多条新闻组成，新闻总数为{total_news_num}条，每条新闻内容之间以|分隔，输出{num}条新闻内容组成的字符串，仍以|分隔。

多个新闻内容字符串：{news_list_string}

要求：
1. 请将输入的多个新闻内容进行删除，保留{num}条新闻内容。
2. 删除内容不像一条新闻的新闻，优先保留这两天刚发生的新闻
3. 删除内容错误无效的新闻，删除内容相近的新闻，删除过长或者过短的新闻。
4. 输出也是字符串，字符串由{num}条新闻内容组成，每条新闻内容之间以|分隔。
5. 输出内容只包含新闻内容，不包含任何其他内容，字符串头尾的'符号请删除"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2500
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
            "model": MODEL_NAME,
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
                if result is not None:
                    processed_news.append(result)                    
                    break  # 成功处理，跳出重试循环
                else:
                    time_flag += 1
                if time_flag > 3:
                    print(f"处理新闻失败，跳过")
                    break

            except Exception as e:
                time_flag += 1        
        # 在每次请求之间添加延时
        time.sleep(1 + time_flag * 3)
    
    return processed_news

def generate_context():
    test_news = get_news_list()
    if test_news is None:
        print("新闻获取失败")
        return None

    result_news = []
    return_news = []
    
    for group_index, news_group in enumerate(test_news):
        news_list = process_news_list(news_group)
        if(len(news_list) >= NEWS_NUM[group_index]):
            result_news.append(news_list)
        else:
            print(f"{NEWS_TYPE[group_index]}新闻数量不足")
            return None

    for index, item in enumerate(result_news):
        retry_count = 0
        while True:
            news_list = choose_news(item, NEWS_NUM[index])
            if news_list is not None:
                return_news.append(news_list)
                break
            else:
                retry_count += 1
                time.sleep(2 + retry_count * 3)  # 失败后等待2秒再重试

    return return_news


new_list = ['2月12日元宵节，一轮圆月高悬，银辉洒满哈尔滨，亚冬之城在冰雪大世界、索菲亚教堂、亚布力等地熠熠生辉。',
'我国科研团队在福建“政和动物群”发现距今1.5亿年的鸟类化石“政和八闽鸟”，这是目前已知最早的鸟类之一，也是唯一确切的侏罗纪鸟类。研究表明，政和八闽鸟的体形接近凤头鹦鹉，体重约100多克，生活在湖边沼泽环境。该发现将现代鸟类身体构型的出现时间提前近2000万年，改写了鸟类演化历史。相关成果发表于国际学术期刊《自然》。',
'中国南北方的历史文化街区正经历传统与现代的融合变革，如北京白塔寺通过“再生计划”引入现代文化产业，深圳观澜古墟修缮后成为客家文化与现代商业结合的历史文化街区，展现了文化传承与发展的新气象。',
'大秦铁路全长653公里，自1985年开通以来，以不到全国铁路营业总里程的0.5%完成了全路1/5的煤运量，日均运量达120万吨，支撑了全国2/3的发电与民生供暖需求，被誉为“能源脊梁”。作 为国家能源运输的“战略动脉”，大秦铁路在改革开放和经济飞速发展中发挥了重要作用，见证了无数大秦人的奉献与奇迹。',
'2月11日，北京西站返程客流高峰中，河北姚女士带回驴肉寄托乡愁，重庆高先生携火锅底料传递家乡味道，湖北王先生带蜜桔分享湖北特色，展现了中国人对传统、乡愁和感情的坚守，以 及对新年的美好期望。',
'金沙江上的叶巴滩水电站建设团队成功攻克高寒高海拔地区冬季混凝土浇筑温控防裂世界级难题，大坝至今未出现任何裂缝，挑战了“无坝不裂”的工程难题，展现了卓越的技术实力。',
'今年春节档电影《哪吒之魔童闹海》票房突破94.81亿元，位居全球单一市场、中国影史及动画电影票房榜首，观众满意度达87.3分。影片角色数量为第一部的3倍，特效镜头近2000个，主创团队4000余人，片尾出现近140家中国动画公司，展现了中国动画电影的崛起。',
'2025年中国航天计划密集，包括发射两艘载人飞船、一艘货运飞船，启动天问二号小行星探测任务，推进多型新研火箭和商业火箭首飞。中国载人月球探测任务登月服命名为“望宇”，月球车命名为“探索”，计划2030年前实现载人登月。长征八号改火箭首飞成功，标志我国新一代运载火箭家族再添新成员。',
'中国科学院遗传与发育生物学研究所科研团队首次从高粱中发现两个关键基因SbSLT1和SbSLT2，通过基因编辑技术显著提高高粱对寄生植物独脚金的抗性，寄生率降低67%-94%，产量损失减少49%-52%，为全球粮食安全提供重要解决方案。',
'近日，“神医”“神药”非法广告伪装成正规报刊在农村地区散布，误导村民。这些虚假广告模仿新闻报道形式，声称有治疗奇效，实则骗局。有关部门需加强监管，打击非法医药广告，净化市场秩序，防止农村老人受骗。',
'春节期间，粮食浪费现象依然存在，部分顾客和餐厅因“面子”和“吉利”观念导致大量剩菜。国家已出台反食品浪费法并开展专项行动，呼吁勤俭节约与传统文化相结合，杜绝浪费行为。',
'新华社报道涉及多个主题，包括河南“重建科学院”改革、火箭创新、AI声音滥用现象调查、徽州鱼灯文化体验、亚冬会元宵节活动、阿勒泰冰雪故事及长三角文化潮流等。',
'国家安全机关近日打掉一个冒充国安干警实施诈骗的犯罪团伙，团伙头目李林伪造身份、虚构关系链，诱骗多人参与所谓“高额返利”项目。国安机关提示公众提高警惕，核实身份信息，不轻 信陌生来电或“内幕活动”，发现线索可通过12339举报。',
'第39届秦淮灯会自1月21日亮灯以来，吸引大量游客，位列全国新春灯会“第一梯队”。秦淮灯彩已有1700多年历史，自1986年恢复举办以来累计吸引2亿人次。灯会融合传统技艺与科技，重现明代市井繁华，成为中式浪漫的具象化表达。',
'春节期间，成都及周边游客被“挖水晶”活动吸引，但专家指出，游客挖到的多为方解石而非水晶。方解石与水晶外观相似，但成分和用途不同，方解石主要用于水泥、环保等领域，而水晶则用于珠宝和工艺品制作。',
'第九届亚洲冬季运动会将于2月14日闭幕，哈尔滨旅游热度飙升，东北特色美食冻梨“出圈”。专家介绍，制作冻梨需经过贮藏、冷冻、解冻三步骤，选用抗寒、晚熟梨品种，如“冬蜜梨”，其 皮薄肉厚、酸甜适口，适合冻梨制作。',
'辽宁省葫芦岛市兴城市年均生产1.7亿件（套）泳装，销往全球140多个国家和地区，年产值达150亿元，占国内市场份额40%以上，国际市场份额25%以上。兴城有1300余户泳装企业，三分之一人口从事泳装相关工作，2024年被评为辽宁省工业单项（泳装）冠军培育县。',
]

# retry_count = 0
# while True:
#     news = choose_news(new_list, 10)
#     if news is not None:
#         print(len(news))
#         print(news)
#         break
#     else:
#         retry_count += 1
#         time.sleep(2 + retry_count * 2)  # 失败后等待2秒再重试


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

# url = "https://api.siliconflow.cn/v1/chat/completions"
# API_KEY = "sk-kienwrrlpkscoeydqofzfgjmewvmdmmfzadavuoupqpyeosx"

# payload = {
#     "model": MODEL_NAME,
#     "messages": [
#         {
#             "role": "user",
#             "content": "中国大模型行业2025年将会迎来哪些机遇和挑战？"
#         }
#     ],
#     "stream": False,
#     "max_tokens": 512,
#     "stop": ["null"],
#     "temperature": 0.7,
#     "top_p": 0.7,
#     "top_k": 50,
#     "frequency_penalty": 0.5,
#     "n": 1,
#     "response_format": {"type": "text"},
#     "tools": [
#         {
#             "type": "function",
#             "function": {
#                 "description": "<string>",
#                 "name": "<string>",
#                 "parameters": {},
#                 "strict": False
#             }
#         }
#     ]
# }
# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# response = requests.request("POST", url, json=payload, headers=headers)

# print(response.text)
# print(response.status_code)
