from GetNews import  NEWS_TYPE

def generate_wxml(news_data):

    news_wxml = [[] for _ in range(6) ]

    if len(news_data) == 0 or news_data is None:
        news_data = [
            [
                "国家发展改革委部署2025年春耕化肥保供稳价工作，要求加强生产、运输、储备、进出口、市场监管和农化服务，确保春耕期间化肥供应充足、价格稳定。",
                "2月9日，第九届亚冬会短道速滑女子3000米接力A组决赛在哈尔滨举行，中国队夺得冠军。选手公俐、张楚桐、王欣然、范可新表现出色，韩国队选手金吉莉在比赛中摔倒。中国队与教练共同庆祝胜利",
                "2月9日，第九届亚冬会短道速滑女子3000米接力A组决赛在哈尔滨举行，中国队夺得冠军。选手公俐、张楚桐、王欣然、范可新表现出色，韩国队选手金吉莉在比赛中摔倒。中国队与教练共同庆祝胜利",
                "第四条新闻..."
            ],
            [
                "国际。",
                "第二条新闻...",
                "第三条新闻...",
                "第四条新闻..."
            ],
            [
                "财经。",
                "第二条新闻...",
                "第三条新闻...",
                "第四条新闻..."
            ],
            [ 
                "2月9日，第九届亚冬会短道速滑女子3000米接力A组决赛在哈尔滨举行，中国队夺得冠军。选手公俐、张楚桐、王欣然、范可新表现出色，韩国队选手金吉莉在比赛中摔倒。中国队与教练共同庆祝胜利",
                "科威特选手法里斯·阿洛巴德在亚冬会高山滑雪项目中表现出色，希望带动滑雪运动在科威特的发展。沙特选手贾德·法尔胡德也参与比赛，沙特作为下届亚冬会东道主，计划从哈尔滨汲取办赛经验。",
                "第三条新闻...",
                "第四条新闻..."
            ],
            [
                "生活服务。",
                "第二条新闻...",
                "第三条新闻...",
                "第四条新闻..."
            ],
            [
                "健康养生。",
                "第二条新闻...",
                "第三条新闻...",
                "第四条新闻..."
            ]
        ]
    
    for group_index, group_news in enumerate(news_data):
        news_wxml[group_index] = f"""<view style="display: block; margin: 10px 0; font-size: 16px; line-height: 1.6;">"""
        for index, item in enumerate(group_news):
            news_wxml[group_index] += f"""<span style = "display:block;"><span style="color:#007aff; font-weight: bold;">{index + 1}）</span>{item}</span>"""
        news_wxml[group_index] += f"""</view>"""

    title_colors = ['#007aff', '#34c759', '#ff9500', '#ff2d55', '#5856d6', '#af52de']
    block_news = [[] for _ in range(6)]
    
    for index, item in enumerate(NEWS_TYPE):
        block_news[index] = f"""
            <view style="font-size: 20px; margin: 10px 0;">
                <text style="display: inline-block; background-color: {title_colors[index]}; color: #fff; padding: 5px 15px; border-radius: 4px;margin-top: 0px; margin-bottom: 10px;">{item}</text>
            </view>"""
        block_news[index] += f"""
            <view style="display: block; width: calc(99% - 40px); margin-left: 0px; vertical-align: top; align-self: flex-start; flex: 0 0 auto; height: auto;border-style: solid; border-width: 2px; border-color: rgb(200, 215, 255); border-radius: 12px; overflow: hidden; box-shadow: rgb(200, 215, 255) 4px 3px 0px 0px;padding: 15px; margin-top: 0px; margin-bottom: 15px;">
                <view style="margin: 15px 0;">
                    {news_wxml[index]}
                </view>
            </view>"""
    
    block_news_wxml = ""
    for item in block_news:
        block_news_wxml += item

    wxml =f"""
        <view> 
        <view style="line-height: 1.5; color: #333;background-color: #f9f9f9;padding: 10px;">  
            {block_news_wxml}
        </view>
        </view>
        """

    with open("output.html", "w", encoding="utf-8") as file:
        file.write(wxml)

    return wxml
