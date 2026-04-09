#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制使用环境变量 Cookie 运行，跳过所有登录验证
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# 配置
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK', '')
BILI_COOKIE = {
    'DedeUserID': os.environ.get('BILI_DEDEUSERID', ''),
    'SESSDATA': os.environ.get('BILI_SESSDATA', ''),
    'bili_jct': os.environ.get('BILI_JCT', '')
}

# 检查配置
if not all([FEISHU_WEBHOOK, BILI_COOKIE['DedeUserID'], BILI_COOKIE['SESSDATA'], BILI_COOKIE['bili_jct']]):
    print("❌ 错误：环境变量未设置完整")
    print(f"FEISHU_WEBHOOK: {'已设置' if FEISHU_WEBHOOK else '未设置'}")
    print(f"DEDEUSERID: {'已设置' if BILI_COOKIE['DedeUserID'] else '未设置'}")
    print(f"SESSDATA: {'已设置' if BILI_COOKIE['SESSDATA'] else '未设置'}")
    print(f"BILI_JCT: {'已设置' if BILI_COOKIE['bili_jct'] else '未设置'}")
    sys.exit(1)

print(f"✅ 环境变量检查通过，用户ID: {BILI_COOKIE['DedeUserID']}")

# 构造请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://t.bilibili.com/',
    'Cookie': f"DedeUserID={BILI_COOKIE['DedeUserID']}; SESSDATA={BILI_COOKIE['SESSDATA']}; bili_jct={BILI_COOKIE['bili_jct']}"
}

def send_feishu(text, title="B站监控"):
    """发送飞书消息"""
    if not FEISHU_WEBHOOK:
        return
    
    data = {
        "msg_type": "text",
        "content": {
            "text": f"{title}\n\n{text}"
        }
    }
    
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=data, timeout=10)
        print(f"飞书推送结果: {resp.status_code}")
    except Exception as e:
        print(f"飞书推送失败: {e}")

def get_followed_dynamics():
    """获取关注动态"""
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all"
    params = {
        'type': 'all',
        'page': 1,
        'offset': ''
    }
    
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = resp.json()
        
        if data.get('code') != 0:
            print(f"❌ API 返回错误: {data.get('message', '未知错误')}")
            # 如果是 -101 表示 Cookie 确实无效
            if data.get('code') == -101:
                print("Cookie 可能已过期，请检查 SESSDATA")
            return []
        
        items = data.get('data', {}).get('items', [])
        print(f"✅ 获取到 {len(items)} 条动态")
        return items
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def check_new_videos():
    """检查新视频"""
    print(f"\n🔍 开始检查: {datetime.now()}")
    
    items = get_followed_dynamics()
    if not items:
        return
    
    # 这里简化处理，实际应该对比上次检查记录
    # 现在只推送最新的1条作为测试
    for item in items[:1]:
        modules = item.get('modules', {})
        author = modules.get('module_author', {})
        dynamic = modules.get('module_dynamic', {})
        
        name = author.get('name', '未知UP')
        pub_time = author.get('pub_time', '')
        desc = dynamic.get('desc', {}).get('text', '')[:50]
        
        msg = f"UP主: {name}\n时间: {pub_time}\n内容: {desc}"
        print(f"📢 发现动态: {msg}")
        send_feishu(msg, "B站新动态提醒")

if __name__ == '__main__':
    print("=== B站监控强制运行模式 ===")
    check_new_videos()
    print("=== 检查完成 ===")
