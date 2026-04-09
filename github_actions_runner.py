#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 运行入口
读取环境变量中的 Cookie 并运行监控
"""

import os
import json
import sys

# 先创建 cookie 文件供原脚本使用
def prepare_cookies():
    cookies = {
        "DedeUserID": os.environ.get('BILI_DEDEUSERID', ''),
        "DedeUserID__ckMd5": "80b26d921c95178f",
        "SESSDATA": os.environ.get('BILI_SESSDATA', ''),
        "bili_jct": os.environ.get('BILI_JCT', '')
    }
    
    # 检查是否获取到所有值
    if not all([cookies['DedeUserID'], cookies['SESSDATA'], cookies['bili_jct']]):
        print("错误：环境变量未设置完整，请检查 Secrets")
        print(f"DEDEUSERID: {'已设置' if cookies['DedeUserID'] else '未设置'}")
        print(f"SESSDATA: {'已设置' if cookies['SESSDATA'] else '未设置'}")
        print(f"BILI_JCT: {'已设置' if cookies['bili_jct'] else '未设置'}")
        sys.exit(1)
    
    # 保存到 cookies.json（原脚本会读取的文件）
    with open('cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    
    print(f"Cookie 已保存到 cookies.json")
    print(f"用户ID: {cookies['DedeUserID']}")
    return True

# 创建配置文件
def prepare_config():
    config = {
        "feishu_webhook": os.environ.get('FEISHU_WEBHOOK', ''),
        "check_interval_minutes": 5,
        "followed_dynamic_types": ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"],
        "followed_mids": []
    }
    
    if not config['feishu_webhook']:
        print("错误：FEISHU_WEBHOOK 未设置")
        sys.exit(1)
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"配置已保存到 config.json")
    return True

if __name__ == '__main__':
    print("=== Bilibili Notifier for GitHub Actions ===")
    
    # 准备环境
    prepare_cookies()
    prepare_config()
    
    print("\n准备完成，开始运行主程序...")
    
    # 导入并运行原脚本的主逻辑
    # 我们需要修改原脚本的运行方式，避免它进入二维码登录流程
    
    # 方案：直接执行原脚本，但让它读取我们创建的 cookie 文件
    import subprocess
    result = subprocess.run([sys.executable, 'bilibili_followed_dynamics.py'], 
                          capture_output=False)
    sys.exit(result.returncode)
