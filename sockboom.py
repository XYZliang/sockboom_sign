import requests
import json
import os
import time
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
email = os.environ["email"]
passwd = os.environ["passwd"]

# 设置一个全局参数存储打印信息，最后好推送
contents = ''


def output(content):
    global contents
    contents += '\n'+content
    print(content)


def sign(header):
    url = 'https://sockboom.art/auth/login?email='+email+'&passwd='+passwd+''
    response = requests.post(url=url, headers=header, verify=False)
    sign_message = json.loads(response.text)['msg']
    user = json.loads(response.text)['user']
    output('  [+]'+sign_message+'，用户：'+user)
    cookie = response.headers
    cookie_uid = cookie['Set-Cookie'].split('/')[0].split(';')[0]
    cookie_email = cookie['Set-Cookie'].split(
        '/')[1].split(';')[0].split(',')[1]
    cookie_key = cookie['Set-Cookie'].split('/')[2].split(';')[0].split(',')[1]
    cookie_ip = cookie['Set-Cookie'].split('/')[3].split(';')[0].split(',')[1]
    cookie_expire_in = cookie['Set-Cookie'].split('/')[4].split(';')[
        0].split(',')[1]
    Cookie = cookie_uid+';'+cookie_email+';' + \
        cookie_key+';'+cookie_ip+';'+cookie_expire_in
    return Cookie


def user_centre(cookie):  # 用户中心
    url = 'https://sockboom.art/user'
    headers = {
        'Cookie': cookie
    }
    response = requests.get(url=url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')  # 解析html页面
    # 获取个人用户信息
    pims = soup.select('.dash-card-content h3')
    pim = [pim for pim in pims]
    output('  [+]用户等级:'+pim[0].string)
    output('  [+]账户余额:'+pim[1].text.split('\n')[0])
    output('  [+]在线设备:'+pim[2].text.split('\n')[0])
    output('  [+]宽带速度:'+pim[3].string)
    # 获取流量信息
    flows = soup.select('span[class="pull-right strong"]')
    flow = [flow.string for flow in flows]
    output('  [+]总流量:'+flow[0])
    output('  [+]使用流量:'+flow[1])
    output('  [+]剩余流量:'+flow[2])
    output('  [+]可用天数:'+flow[3])
    return headers


def checkin(headers):
    url = 'https://sockboom.art/user/checkin'
    response = requests.post(url=url, headers=headers, verify=False)
    msg = json.loads(response.text)['msg']
    output('  [+]签到信息:'+msg)


def dingtalk(webhook):  # 钉钉消息推送
    webhook_url = webhook
    dd_header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    global contents
    dd_message = {
        "msgtype": "text",
        "text": {
            "content": f'SockBoom每日续命信息通知！\n{contents}'
        }
    }
    r = requests.post(url=webhook_url, headers=dd_header,
                      data=json.dumps(dd_message))
    if r.status_code == 200:
        output('  [+]钉钉消息已推送，请查收  ')


def server(sendkey):
    url = 'https://sctapi.ftqq.com/'+sendkey+'.send'
    message = contents
    message = message.replace("\n", "\n\n")
    title = 'SockBoom每日续命信息通知！'
    data = {'title': title.encode('utf-8'), 'desp': message.encode('utf-8')}
    res = requests.post(url=url, data=data)
    serverdata = json.loads(res.text)
    if serverdata["data"]["error"] == "SUCCESS":
        pushid = serverdata["data"]["pushid"]
        readkey = serverdata["data"]["readkey"]
        url = "https://sctapi.ftqq.com/push?id=" + pushid + "&readkey=" + readkey
        i = 1
        wxstatus = ""
        wxok = False
        while i < 60 and wxok is False:
            time.sleep(0.25)
            res = requests.get(url=url)
            serverstatusdata = json.loads(res.text)
            wxstatus = str(serverstatusdata["data"]["wxstatus"])
            i = i + 1
            if len(wxstatus) > 2:
                wxok = True
        if wxok:
            print("SERVER发送成功")
        else:
            print("SERVER发送失败")


def main():
    cookie = sign(header)
    headers = user_centre(cookie)
    checkin(headers)
    try:
        dingwebhook = os.environ["webhook"]  # 钉钉机器人的 webhook
        if(len(dingwebhook)) > 1:
            dingtalk(dingwebhook)
        else:
            raise KeyError
    except KeyError:
        print("没有在Repository secrets配置钉钉机器人的‘webhook’,跳过发送钉钉推送")
    try:
        serverkey = os.environ["serverkey"]  # server酱的 webhook
        if(len(serverkey)) > 1:
            server(serverkey)
        else:
            raise KeyError
    except KeyError:
        print("没有在Repository secrets配置server酱的‘serverkey’,跳过发送server酱推送")


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    main()
