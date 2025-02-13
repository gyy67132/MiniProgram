import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import re
import time

NEWS_TYPE = ['国内', '国际', '财经', '文体娱乐', '生活服务', '健康养生']
NEWS_NUM = [10,8,5,4,5,2]

from datetime import datetime, timedelta
import re

from datetime import datetime
import re

def check_news_date(link, news_soup):
    """检查新闻是否为今天发布"""
    today = (datetime.now()).date()
    today_str = today.strftime('%Y-%m-%d')  # 2024-02-12
    today_compact = today.strftime('%Y%m%d') # 20240212
    
    try:
        # 1. 获取页面所有文本
        page_text = str(news_soup)  # 包含HTML标签的完整文本
        
        # 2. 检查所有可能的日期格式
        date_patterns = [
            # URL中的日期
            rf'/({today.year})-({today.month:02d})/({today.day:02d})',  # /2024-02/12
            rf'/({today_compact})',  # /20240212
            
            # 正文中的日期格式
            rf'{today.year}年{today.month}月{today.day}日',  # 2024年2月12日
            rf'{today.year}-{today.month:02d}-{today.day:02d}',  # 2024-02-12
            rf'{today.year}/{today.month:02d}/{today.day:02d}',  # 2024/02/12
            rf'{today.year}\.{today.month:02d}\.{today.day:02d}'  # 2024.02.12
        ]
        
        # 3. 在URL和页面内容中查找今天的日期
        for pattern in date_patterns:
            if re.search(pattern, link) or re.search(pattern, page_text):
                return True
                    
        return False
        
    except Exception:
        return False


def get_today_news(urls):
   
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
                '.focus-news',  # 焦点新闻
            

                # 列表类选择器
                'ul.dataList li a',           # 新华网等
                'ul.newsList li a',           # 常见新闻列表
                'ul.list li a',               # 通用列表
                'div.list a',                 # 通用列表容器
                '.news-list a',               # 新闻列表
                '.articleList a',             # 文章列表
                
                # 新闻内容区选择器
                'div.news_box a',             # 新闻盒子
                'div.content a',              # 内容区
                'div.article a',              # 文章区
                '.main-news a',               # 主要新闻区
                
                # 标题类选择器
                'a.title',                    # 标题链接
                '.news-title',                # 新闻标题
                '.article-title',             # 文章标题
                'h3.title a',                 # 标题标签
                
                # 特定位置新闻选择器
                '.top-news a',                # 头条新闻
                '.focus-news a',              # 焦点新闻
                '.latest-news a',             # 最新新闻
                
                # 分类新闻选择器
                '.domestic a',                # 国内新闻
                '.international a',           # 国际新闻
                '.politics a',                # 政治新闻
                '.finance a',                 # 财经新闻
                
                # 通用容器选择器
                '.container a',               # 通用容器
                '.wrapper a',                 # 通用包装器
                '.main a',                    # 主要区域
                
                # 特定网站选择器
                '.xinhua-news a',             # 新华网
                '.cctv-news a',              # 央视网
                '.ce-news a'                  # 中国经济网
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    for item in items:
                        if item.get('href') and item.get_text().strip():
                            news_list.append(item)
            
            print(f"找到 {len(news_list)} 条可能的新闻，开始筛选...")

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
                    
                    
                    # 在get_today_news函数中替换原来的日期检查部分：
                    try:
                        news_response = requests.get(link, headers=headers, timeout=5)
                        news_response.encoding = 'utf-8'
                        news_soup = BeautifulSoup(news_response.text, 'html.parser')
                        
                        if not check_news_date(link, news_soup):
                            #print(f"{link}新闻 {title} 不是当天新闻，跳过")
                            continue
                        
                    except Exception as e:
                        print(f"获取新闻详情页失败: {str(e)}")
                        continue

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
    """获取新闻内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
        # 定义错误页面的关键词
        error_keywords = [
            '页面不存在',
            '已被删除',
            '404',
            'Not Found',
            '访问的页面不存在',
            '无法找到页面',
            '页面错误',
            '无法访问'
        ]
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        
        # 检查响应状态
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面标题是否包含错误关键词
        title = soup.title.string if soup.title else ''
        if any(keyword in title for keyword in error_keywords):
            return None
            
        content_selectors = [
            'div.article-content',
            'div.content',
            'div.article',
            'div.main-content',
            'div.text',
            'div.detail',
            '#article',
            '#content',
            '.article-body',
            '.news-text',
            'div.contentMain',
            'div.article_content',
            'div.news-content',
            'div.main'
        ]
        
        # 尝试每个选择器
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # 清理内容
                [x.extract() for x in content_div.find_all(['script', 'style', 'iframe'])]
                content = content_div.get_text(strip=True)
                # 检查内容是否包含错误关键词
                if len(content) > 100 and not any(keyword in content for keyword in error_keywords):
                    return content
        
        # 尝试段落
        paragraphs = soup.find_all(['p'])
        if paragraphs:
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs 
                               if len(p.get_text(strip=True)) > 20])
            if len(content) > 100 and not any(keyword in content for keyword in error_keywords):
                return content
                
        # 最后尝试正文
        body = soup.find('body')
        if body:
            [x.extract() for x in body.find_all(['script', 'style', 'iframe', 'header', 'footer', 'nav'])]
            content = body.get_text(strip=True)
            if len(content) > 100 and not any(keyword in content for keyword in error_keywords):
                return content
                
        return None
        
    except Exception as e:
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
            "http://www.news.cn/domestic/",             # 国内新闻
            "http://www.xinhuanet.com/politics/",    # 时政频道（主要国内新闻源）
            #"http://www.news.cn/politics/",          # 时政频道备用地址
            "http://www.news.cn/local/",             # 地方新闻
            #"http://www.xinhuanet.com/local/",       # 地方新闻备用地址
            "https://www.qq.com/"
        ],
        [
            "http://www.cctv.com/cctv4/",
            "http://www.news.cn/world/",      # 国际频道
            #"http://finance.ifeng.com/",
            #"https://news.qq.com/ch/world/",
            "http://intl.ce.cn/",
            "https://www.chinanews.com/world/"
        ],
        [
            "http://www.news.cn/finance/",   # 财经频道（备用地址）
            "http://finance.people.com.cn/",
            "https://finance.cctv.com/",
            #"http://www.ce.cn/",
            "https://finance.qq.com/",
            "http://finance.ce.cn/",
            "https://economy.gmw.cn/"
            #"https://cn.chinadaily.com.cn/business/"
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
            "http://www.xinhuanet.com/house/"
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
        
        news = get_today_news(url_group)
        print(f"\n {group_index + 1} 组共获取到 {len(news)} 条新闻")
        
        result_news_group = []
        
        count = 0
        
        for index,item in enumerate(news):
            content = get_news_content(item['link'])
            if content and is_chinese_text(item['title']) and "页面不存在" not in content:
                result_news_group.append(content[:1000])
                count += 1
                # print(f"\n{count}.标题： {item['title']}")
                print(f"  链接：{item['link']}")
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