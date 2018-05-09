# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Created on Tue Apr 17 11:01:28 2018

@author: Administrator
"""
import urllib
import json

# 设置一个退出程序的出口
isOut = False

# 不断调用爬取翻译页面的功能
# 直到isOut被设置为True，退出程序


def query(keys):
    while True:
        if isOut == True:
            break

        # 假定用户输入“CloseMe”，则退出
        key = keys
        if key == "CloseMe":
            isOut = True
            continue  # 回到循环开始处，然后结果条件满足退出

        # 做真正的查询操作
        url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null"

        # 构造headers
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
                   "X-Requested-With": "XMLHttpRequest",
                   "Accept": "application/json, text/javascript, */*; q=0.01",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                   }

        # 把form数据转规范化，然后post给服务端
        formdata = {
            "i": key,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": "1523933959290",
            "sign": "248f5d216c45a64c38a3dccac0f4600d",
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTIME",
            "typoResult": "false"
        }
        data = bytes(urllib.parse.urlencode(
                     formdata),
                     encoding="utf-8")
        # 给服务器发送post请求
        req = urllib.request.Request(url,
                                     data,
                                     headers,
                                     method="POST")
        response = urllib.request.urlopen(req)
        info = response.read().decode("utf-8")
        jsonLoads = json.loads(info)
        return jsonLoads['translateResult'][0][0]["tgt"]
