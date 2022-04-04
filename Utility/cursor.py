import pymysql

class Cursor():
    def __init__(self, host="localhost", user="", passwd="", charset='utf8') -> None: 
        self.host = host 
        self.user = user 
        self.passwd = passwd 
        self.charset = charset 
        
    def get_cursor(self, db_name):
        conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=db_name, charset=self.charset)
        return conn, conn.cursor()