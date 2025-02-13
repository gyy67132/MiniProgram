import schedule
import time
from UploadArticle import job

if __name__ == "__main__":
    # 每天10点运行一次
    schedule.every().day.at("22:27").do(job)
    
    print("定时任务已启动，等待执行...")
    while True:
        schedule.run_pending()
        time.sleep(1)
