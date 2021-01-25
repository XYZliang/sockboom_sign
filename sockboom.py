import requests
import json
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


webhook = 'https://oapi.dingtalk.com/robot/send?access_token=4978dbdd11859e0e4a036d517e8219e1ec4d06a3ad9aa968d10abe947d409e61' # 钉钉机器人的 webhook
header={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
email='753476038%40qq.com'
passwd='l753476038'
push=0      # 1 为钉钉推送 其他为不推送
global content  #设置一个全局参数存储打印信息，最后好推送
contents=''
def output(content): 
    global contents
    contents+='\n'+content
    print(content)

def sign(header):
    url='https://sockboom.art/auth/login?email='+email+'&passwd='+passwd+''
    response = requests.post(url=url,headers=header,verify=False)
    sign_message=json.loads(response.text)['msg']
    user=json.loads(response.text)['user']
    output('  [+]'+sign_message+'，用户：'+user)
    cookie=response.headers
    cookie_uid=cookie['Set-Cookie'].split('/')[0].split(';')[0]
    cookie_email=cookie['Set-Cookie'].split('/')[1].split(';')[0].split(',')[1]
    cookie_key=cookie['Set-Cookie'].split('/')[2].split(';')[0].split(',')[1]
    cookie_ip=cookie['Set-Cookie'].split('/')[3].split(';')[0].split(',')[1]
    cookie_expire_in=cookie['Set-Cookie'].split('/')[4].split(';')[0].split(',')[1]
    Cookie=cookie_uid+';'+cookie_email+';'+cookie_key+';'+cookie_ip+';'+cookie_expire_in
    return Cookie
def user_centre(cookie):   #用户中心
    url='https://sockboom.art/user'
    headers={
    'Cookie':cookie
    }
    response = requests.get(url=url,headers=headers,verify=False)
    soup = BeautifulSoup(response.text, 'html.parser') #解析html页面
    #获取个人用户信息
    pims= soup.select('.dash-card-content h3')
    pim=[pim for pim in pims]
    output('  [+]用户等级:'+pim[0].string)
    output('  [+]账户余额:'+pim[1].text.split('\n')[0])
    output('  [+]在线设备:'+pim[2].text.split('\n')[0])
    output('  [+]宽带速度:'+pim[3].string)
    #获取流量信息
    flows = soup.select('span[class="pull-right strong"]')
    flow=[flow.string for flow in flows]
    output('  [+]总流量:'+flow[0])
    output('  [+]使用流量:'+flow[1])
    output('  [+]剩余流量:'+flow[2])
    output('  [+]可用天数:'+flow[3])
    return headers
def checkin(headers):
    url='https://sockboom.art/user/checkin'
    response = requests.post(url=url,headers=headers,verify=False)
    msg=json.loads(response.text)['msg']
    output('  [+]签到信息:'+msg)

def dingtalk():       #钉钉消息推送
    webhook_url=webhook
    dd_header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
        }
    global contents
    dd_message = {
        "msgtype": "text",
        "text": {
            "content":f'SockBoom每日续命信息通知！\n{contents}'
                }
        }
    r = requests.post(url=webhook_url, headers=dd_header, data=json.dumps(dd_message))
    if r.status_code==200:
        output('  [+]钉钉消息已推送，请查收  ')

def main():
    cookie=sign(header)
    headers=user_centre(cookie)
    checkin(headers)
    if push==1:
        dingtalk()
def main_handler(event, context):
    return main()
if __name__ == '__main__':
    main()
