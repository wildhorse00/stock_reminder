#coding=utf-8
import tushare as ts
import time
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

PERIOD = 3
MAX_EMAIL_CNT = 3
from_addr = 'simplaurel@163.com'
pswd = ''
to_addr = 'bsymlxl@126.com'

#600887 : 伊利股份
#000651 ：格力电器
#603259 ：药明康德
stock_list = ['600887','000651','603259']
tar_high_price = [27.,42.,90.]
tar_low_price  = [22.,35.,75.]

def is_in_trade_time():
    cur = time.strftime('%H%M%S',time.localtime())
    if(cur > '091500' and cur < '113000') or (cur > '130000' and cur < '150000'):
        return 1
    return 0

def get_stock_price(stock_list):
    df = ts.get_realtime_quotes(stock_list)
    return df[['code','name','date','time','pre_close','high','low','amount','price']]

def send_email(from_addr,password,to_addr,smtp_server,message):
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr(( \
            Header(name, 'utf-8').encode(), \
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))
    
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'观察者 <%s>' % from_addr)
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header(u'交易信号','utf-8').encode()
    
    server = smtplib.SMTP_SSL(smtp_server, 465)
    #server.starttls()
    #server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()        
    print('mail sent done.')

def calc_stratagy(sinfo,hprice,lprice):
    msg = ''
    for index,row in sinfo.iterrows():
        #print index,float(row['price']),lprice[index]
        if float(row['price']) < lprice[index] or float(row['price']) > hprice[index]:
                msg += '[{0}]当前股价为:{1}，达到设定{2}价格{3}.\n'.format(\
                row['name'],row['price'],\
                '买入' if float(row['price']) < lprice[index] else '卖出',\
                lprice[index] if float(row['price']) < lprice[index] else hprice[index])
    return msg 

def main():
    sent_cnt = 0
    while(1):
        if(is_in_trade_time()):
            pcs = get_stock_price(stock_list)
            print(pcs)
            msg = calc_stratagy(pcs,tar_high_price,tar_low_price)
            if msg != '' and sent_cnt < MAX_EMAIL_CNT:
                print('Email sent : \n' + msg)
                send_email(from_addr,pswd,to_addr,'smtp.163.com',msg)
                sent_cnt += 1
            time.sleep(PERIOD)

if __name__ == '__main__':
    main() 
