import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

NEWS_TYPE = ['国内', '国际', '财经', '文体娱乐', '生活服务', '健康养生']
NEWS_NUM = [10,8,5,4,5,2]

def get_xinhua_news(urls):
   
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    today_news = []  # 移到循环外面
    
    for url in urls:
        try:
            print(f"\n开始获取 {url} 的新闻...")
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试更多的选择器
            news_list = []
            selectors = [
                'a',  # 所有链接
                '.news',  # 新闻类
                '.content',  # 内容类
                '.main',  # 主要内容
                '#main',  # 主要内容ID
                '.article',  # 文章类
                '.headline',  # 头条类
                'h1 a',  # h1标签中的链接
                'h2 a',  # h2标签中的链接
                'h3 a',  # h3标签中的链接
                '.top-news',  # 顶部新闻
                '.focus-news'  # 焦点新闻
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    for item in items:
                        if item.get('href') and item.get_text().strip():
                            news_list.append(item)
            
            print(f"找到 {len(news_list)} 条可能的新闻，开始筛选...")
        
            today = datetime.now().strftime('%Y%m%d')  # 获取当前日期，格式如：20240321
            today_dash = datetime.now().strftime('%Y-%m-%d')  # 格式如：2024-03-21

            for news in news_list:
                try:
                    title = news.get_text().strip()
                    link = news.get('href', '')
                    
                    # 基本过滤
                    if not title or not link or len(title) < 10:
                        continue
                        
                    # 确保链接是完整的URL
                    if link.startswith('//'):
                        link = 'http:' + link
                    elif not link.startswith('http'):
                        # 修复URL拼接问题
                        if not link.startswith('/'):
                            link = '/' + link
                        link = 'http://www.news.cn' + link
                    
                    news_time = soup.find(['time', 'span', 'div'], 
                                        class_=['time', 'date', 'publish-time', 'article-time'])
                    if news_time:
                        publish_time = news_time.get_text().strip()
                        if today_dash not in publish_time:
                            continue
                    
                    # 检查链接中是否包含今天的日期
                    #if today not in link.replace('-', '') and today_dash not in link:
                        #continue

                    # 过滤非新闻内容
                    if any(x in title for x in ['视频', '图片', '直播', '登录', '注册', '手机版']):
                        continue
                        
                    if any(x in link for x in ['video', 'photo', 'live']):
                        continue
                    
                    news_item = {
                        'title': title,
                        'link': link,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                    
                    if news_item not in today_news:  # 避免重复新闻
                        today_news.append(news_item)
                        #print(f"找到新闻: {title}")
                    
                except Exception as e:
                    print(f"处理单条新闻时出错: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"处理 {url} 时发生错误: {str(e)}")
            continue
    
    print(f"\n所有源处理完成，共获取到 {len(today_news)} 条有效新闻")
    return today_news

def get_news_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        #print(f"\n正在获取文章内容: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试多个可能的内容选择器
        content_selectors = [
            'div.article-content',  # 标准文章内容
            'div#detail',           # 详情内容
            'div.content',          # 通用内容
            'div.main-content',     # 主要内容
            'div.article',          # 文章区域
            'div#content',          # 内容ID
            'div.text',             # 文本内容
            'div.article-body',     # 文章主体
            'div.main-aticle'       # 另一种文章内容
        ]
        
        # 尝试所有可能的选择器
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # 获取所有段落文本
                paragraphs = content.find_all(['p', 'div'])
                text_content = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 10:  # 过滤掉太短的段落
                        text_content.append(text)
                
                if text_content:
                    #print("成功获取文章内容")
                    return "\n".join(text_content)
        
        # 如果上面的选择器都失败了，尝试获取正文部分
        article_text = []
        # 查找所有可能的段落
        paragraphs = soup.find_all(['p', 'div'], class_=['p-text', 'text', 'article-paragraph'])
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 10:
                article_text.append(text)
        
        if article_text:
            #print("通过段落获取到文章内容")
            return "\n".join(article_text)
            
        #print("无法找到文章内容，返回页面标题")
        # 如果还是找不到内容，至少返回标题
        #title = soup.find('title')
        #return f"只找到标题: {title.text if title else '无标题'}"
        return None
    except Exception as e:
        print(f"获取文章内容时发生错误: {str(e)}")
        return None

def is_chinese_text(text):
    """更严格的中文检测"""
    # 移除常见的标点符号
    text = re.sub(r'[，。！？、：；''""（）【】《》]', '', text)
    # 统计中文字符的数量
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    # 如果中文字符占比超过60%，则认为是中文文本
    return len(text) > 0 and chinese_chars / len(text) > 0.6

def get_news_list():
    print("开始运行新闻采集程序...")

    urls=[
        [
            "http://www.cctv.com/cctv4/",
            "http://www.news.cn/domestic/",   # 国内新闻
            "http://www.xinhuanet.com/politics/",    # 时政频道（主要国内新闻源）
            #"http://www.news.cn/politics/",          # 时政频道备用地址
            #"http://www.news.cn/local/",             # 地方新闻
            #"http://www.xinhuanet.com/local/",       # 地方新闻备用地址
        ],
        [
            "http://www.cctv.com/cctv4/",
            "http://www.news.cn/world/",      # 国际频道
        ],
        [
            "https://finance.cctv.com/",
            "http://www.news.cn/finance/",   # 财经频道（备用地址）
        ],
        [
            #"http://www.news.cn/sports/",     # 体育频道
            "http://www.news.cn/ent/",        # 娱乐频道
            "http://www.news.cn/culture/",    # 文化频道
        ],
        [
            "http://www.news.cn/life/",       # 生活频道
            "http://www.news.cn/food/",       # 美食频道
            "http://www.news.cn/fashion/",    # 时尚频道
            "http://www.news.cn/travel/",     # 旅游频道
        ],
        [
            "http://www.news.cn/health/",     # 健康频道
            "http://www.news.cn/medical/",    # 医疗频道
            "http://www.news.cn/tech/",       # 科技健康
        ]
    ]

    result_news = []

    num = 2

    for group_index, url_group in enumerate(urls):
        
        news = get_xinhua_news(url_group)
        print(f"\n {group_index + 1} 组共获取到 {len(news)} 条新闻")
        
        result_news_group = []
        
        count = 0
        
        for index,item in enumerate(news):
            content = get_news_content(item['link'])
            if content and is_chinese_text(item['title']):
                result_news_group.append(content[:1000])
                count += 1
                # print(f"\n{count}.标题： {item['title']}")
                # print(f"  链接：{item['link']}")
                # print(f"  时间：{item['time']}")
                # print(f"  内容：{content[:100]}...")  # 只显示前200个字符
                # print("-" * 50)
                time.sleep(0.5)  # 添加延时，避免请求过快
            if count >= NEWS_NUM[group_index] * num:  # 获取足够多的新闻供分类使用
                break
        result_news.append(result_news_group)
        print(f"\n {group_index + 1} 组最终获取到 {len(result_news_group)} 条有效新闻")    

    for index in range(len(NEWS_TYPE)):
        if(len(result_news[index]) < NEWS_NUM[index]):
            print(f"{NEWS_TYPE[index]}新闻数量少")
            exit()

    return result_news

#get_news_list()