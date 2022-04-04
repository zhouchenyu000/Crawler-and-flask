import time, datetime, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from Utility.cursor import Cursor
from Utility.log import Logger

crawler_cursor = Cursor()
db, cursor = crawler_cursor.get_cursor("stock_ewom")
db_ai, cursor_ai = crawler_cursor.get_cursor("ai_customerservice_honsec")
db_word, cursor_word = crawler_cursor.get_cursor("stock_sentiword")

logger = Logger(log_name='crawler_errmsg_log')

option = webdriver.ChromeOptions()
option.add_argument('--headless')  #無頭chrome
option.add_argument('--disable-gpu')
option.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),chrome_options=option)

today=str(datetime.date.today())
today=datetime.datetime.strptime(today,'%Y-%m-%d')

class Use_Crawler: #原爬蟲系統約20隻檔案 +Data Preprocessing 共5000行以上code 這裡以三隻爬蟲檔案作為範例
    def __init__(self):
        self.saved_list=[]
    def ptt(self):#static web page
        try:
            web_url='https://www.PTT.cc/bbs/Stock/index.html'
            while (True):
                url_get = requests.get(web_url)
                soup = BeautifulSoup(url_get.text, "html.parser")
                detail=soup.findAll('div',{'class':'r-ent'})
                row = len (detail) -1
                while row >= 0:
                    title=detail[row].select('div.title')[0].text
                    title =title.replace('\n','')
                    if ( '刪除' in title): #被刪除的文章和置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('板規'  in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('盤' and '閒聊' in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('文' and '討論' in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('公告' in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('疫情期間置底閒聊文' in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    if ('文章分類規範改動' in title): #置頂文章要跳過 不然會out of range
                        row = row -1
                        continue
                    else:
                        data_url=detail[row].select('div.title a')[0].get('href')
                        data_url = 'https://www.PTT.cc/'+data_url
                        Year=datetime.datetime.now().strftime('%Y')
                        date=detail[row].select('div.date')[0].text
                        date=Year+'-'+date.strip()
                        date= date.replace('/','-')
                        pagedate=date.split("\r")[0]
                        pagedate=datetime.datetime.strptime(pagedate,'%Y-%m-%d')
                        row = row -1
                        if (today>pagedate):
                            return
                        else:
                            self.saved_list.append(title)
                            if (title not in self.saved_list):
                                cursor.execute("INSERT INTO  `scrapergoogleblog` (`sn` ,`url`  ,`title`,`domain`,`searchday`,`daybygoogle`,`process`,`titlehavekeyword`)VALUES (NULL ,'%s','%s','PTT','%s','%s',  '0',  'Yes')ON DUPLICATE KEY UPDATE `url` ='%s',`title`='%s',`domain`='PTT',`searchday`='%s',`daybygoogle`='%s' ;"%\
                                (data_url,title,str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),date,data_url,title,str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),date))
                                db.commit()

                lastpage = soup.select('a.btn.wide')[1].get('href')
                web_url = 'https://www.PTT.cc/'+lastpage
        except BaseException as e:
            logger.logging_blog_errmsg(step_num='getblog',errormsg = e,bugurl=web_url)  
    
    def cna(self):#dynamic web page 滑到底點選button新增資料
        try:
            web_url ='https://www.cna.com.tw/list/asc.aspx'
            driver.get(web_url)
            time.sleep(2)
            more = driver.find_element_by_css_selector('a.viewBtn.view-more-button.myViewMoreBtn')
            for i in range(5):  #往下滑約5次後不再有新資料
                try:
                    more.click()
                except:
                    pass
                time.sleep(2)
                url_get = driver.page_source
                soup = BeautifulSoup(url_get, "html.parser")
                detail=soup.select('ul.mainList.imgModule li')
                for t in detail:
                    if t.select('div.listInfo')=='':
                        continue
                    title = t.select('div.listInfo h2')[0].text
                    data_url=t.select('a')[0].get('href')
                    date=t.select('div.date')
                    date=date.replace('/','-')
                    date=date[1:11]
                    pagedate=date.split("\r")[0]
                    pagedate=datetime.datetime.strptime(pagedate,'%Y-%m-%d')
                    if not (pagedate == today):
                        return
                    else:
                        self.saved_list.append(title)
                        if (title not in self.saved_list):
                            cursor.execute("INSERT INTO  `scrapergoogleblog` (`sn` ,`url`  ,`title`,`domain`,`searchday`,`daybygoogle`,`process`,`titlehavekeyword`)VALUES (NULL ,'%s','%s','cna','%s','%s',  '0',  'Yes')ON DUPLICATE KEY UPDATE `url` ='%s',`title`='%s' ;"%\
                            (data_url,title,str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),date,data_url,title))
        except Exception as e:
            logger.logging_blog_errmsg(step_num='getblog',errormsg = e,bugurl=web_url)  
    
    def yahoo(self):#dynamic web page 
        try:
            web_url="https://tw.stock.yahoo.com/tw-market"
            driver.get(web_url)
            js = "var q=document.documentElement.scrollTop=100000"
            for i in range(10): #往下滑約10次後不再有新資料
                driver.execute_script(js)  
                time.sleep(2) #給網頁時間去抓資料
                url_get = driver.page_source
                soup = BeautifulSoup(url_get, "html.parser")
                detail=soup.find_all('li',{'class':'js-stream-content Pos(r)'})
                for t in detail:
                    try:
                        tag = t.find('div', {'data-test-locator': 'catlabel'})  #無廣告
                    except:
                        tag = None
                    
                    if (tag != None):
                        title = (t.select('a')[0].text)
                        data_url = t.select('a')[0].get('href')
                        today=str(datetime.date.today())
                        date=today
                        self.saved_list.append(title)
                        if (title not in self.saved_list):
                            cursor.execute("INSERT INTO  `scrapergoogleblog` (`sn` ,`url`  ,`title`,`domain`,`searchday`,`daybygoogle`,`process`,`titlehavekeyword`)VALUES (NULL ,'%s','%s','yahoo','%s','%s',  '0',  'Yes')ON DUPLICATE KEY UPDATE `url` ='%s',`title`='%s' ;"%\
                            (data_url,title,str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),date,data_url,title))
                            db.commit()
        except BaseException as e:
            logger.logging_blog_errmsg(step_num='getblog',errormsg = e,bugurl=web_url)
    

if __name__ == '__main__':
    Use=Use_Crawler()
    Use.ptt()
    Use.cna()
    Use.yahoo()
