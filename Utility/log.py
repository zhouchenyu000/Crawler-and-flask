# -*- coding: UTF-8 -*-
import os, datetime, time, traceback,re,sys
from datetime import date, timedelta, datetime

class Printer():
    def __init__(self, msg, is_debug) -> None:
        self.msg = msg
        self.is_debug = is_debug
        self.print_msg()
    
    def print_msg(self):
        if self.is_debug:
            print(self.msg)

class Logger():
    def __init__(self, log_name, retain_days = 15) -> None:
        self.log_name = log_name # 此log要寫入的名稱
        self.retain_days = retain_days # log欲保留天數
        
    def get_date_text(self, text):
        return re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', text).group()
    
    def checking_dir_exist(self):
        if not os.path.exists(f'./errmsg_log'): # 若資料夾不存在就自動建立
            os.mkdir(f'./errmsg_log')
        if not os.path.exists(f'./errmsg_log/{self.log_name}'): # 若資料夾不存在就自動建立
            os.mkdir(f'./errmsg_log/{self.log_name}')
    
    def check_date(self,step_num,filename):
        if os.path.exists(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_{filename}.txt'):# 檢查檔案是否存在
            ori_log_file = open(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_{filename}', "r")
            lines = ori_log_file.readlines()
            ori_log_file.close()
            start_day = (date.today() - timedelta(days = self.retain_days)).strftime('%Y-%m-%d') # 取得最早保留日期(年月日)
            start_day = datetime.strptime(start_day, '%Y-%m-%d') # 格式轉化 才有辦法比較
            lines = filter(lambda x: start_day <= datetime.strptime(self.get_date_text(x), '%Y-%m-%d'), lines)
            new_log_file = open(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_{filename}', "w+")
            new_log_file.write(''.join(lines))
            new_log_file.close()
    
    def logging_errmsg(self, step_num, errormsg):
        errMsg = traceback.format_exc()
        #Printer(errMsg, is_debug)
        errMsg = errMsg.replace("\n", "")
        self.checking_dir_exist()
        self.check_date(step_num = step_num, filename = 'DetailError.txt') 
        f = open(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_DetailError.txt', 'a+')
        f.writelines(f'Step{step_num}-[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}][Error] -> {errMsg.encode("utf-8")} \n')
        f.close()

    def logging_msg(self, step_num, msg):
        self.checking_dir_exist()
        self.check_date(step_num = step_num, filename = 'Detail.txt')     
        f = open(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_Detail.txt', 'a+')
        f.writelines(f'Step{step_num}-[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]-> {msg}\n')
        f.close()
    
    def logging_blog_errmsg(self, step_num, errormsg, bugurl):
        errMsg = traceback.format_exc()
        #Printer(errMsg, is_debug)
        errMsg = errMsg.replace("\n", "")
        self.checking_dir_exist()
        self.check_date(step_num = step_num, filename = 'DetailError.txt') 
        f = open(f'./errmsg_log/{self.log_name}/Record_{self.log_name}_step{step_num}_DetailError.txt', 'a+')
        f.writelines(f'Step{step_num}-[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}][Error] -> {errMsg}{bugurl} \n')
        f.close()


if __name__ == '__main__':
    logger = Logger(log_name='histock')
    logger.logging_msg(step_num='1', msg='Start')
    logger.logging_errmsg(step_num = '1', errormsg = 'test error massage')
    logger.logging_msg(step_num = '1', msg = 'End')