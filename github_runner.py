#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 运行入口
复用原脚本 bilibili_followed_dynamics 的自评论检测功能
解决 Cookie 失效和状态持久化问题
"""

import os
import sys
import json
import requests

# ========== 配置 ==========
GIST_ID = os.environ.get('GIST_ID')           # 用于存储评论状态
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') # GitHub Token

# 从 Gist 恢复状态文件（避免重复推送）
def restore_state_from_gist():
    if not GIST_ID or not GITHUB_TOKEN:
        print("⚠️ 未配置 Gist，状态将在每次运行后丢失（会重复推送）")
        return
    
    files = ['old_self_comments.json', 'old_bvid.json']
    for fname in files:
        try:
            url = f"https://api.github.com/gists/{GIST_ID}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                gist_files = resp.json().get('files', {})
                if fname in gist_files:
                    content = gist_files[fname]['content']
                    with open(f"bili/{fname}", 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ 从 Gist 恢复 {fname}")
        except Exception as e:
            print(f"⚠️ 恢复 {fname} 失败: {e}")

# 保存状态到 Gist
def save_state_to_gist():
    if not GIST_ID or not GITHUB_TOKEN:
        return
    
    files = ['old_self_comments.json', 'old_bvid.json']
    for fname in files:
        fpath = f"bili/{fname}"
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            url = f"https://api.github.com/gists/{GIST_ID}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"files": {fname: {"content": content}}}
            requests.patch(url, headers=headers, json=data)
            print(f"✅ 已保存 {fname} 到 Gist")
        except Exception as e:
            print(f"⚠️ 保存 {fname} 失败: {e}")

# ========== 准备环境 ==========
os.makedirs('bili', exist_ok=True)
os.makedirs('www/wwwroot', exist_ok=True)

# 恢复之前的状态（避免重复推送同一评论）
restore_state_from_gist()

# 准备 Cookie 文件（原脚本格式）
cookie_data = {
    "DedeUserID": os.environ.get('BILI_DEDEUSERID', ''),
    "DedeUserID__ckMd5": "80b26d921c95178f",  # 占位符，原脚本需要
    "SESSDATA": os.environ.get('BILI_SESSDATA', ''),
    "bili_jct": os.environ.get('BILI_JCT', ''),
    "sid": "github_actions"
}

with open('bili/cookie.txt', 'w', encoding='utf-8') as f:
    f.write(json.dumps(cookie_data, ensure_ascii=False))
print("✅ Cookie 文件已注入")

# ========== 运行原脚本 ==========
import bilibili_followed_dynamics as bili

# 关键：Patch 登录验证，强制通过（避免弹出二维码）
original_cookie_valid = bili.session_cookie.cookie_valid
def forced_cookie_valid(self):
    # 可选：真实验证（如需）
    # 直接返回 True，跳过二维码登录
    return True

bili.session_cookie.cookie_valid = forced_cookie_valid

# 执行（这将触发原脚本的完整流程：获取关注动态 + 检测 UP 主自评论）
print("🚀 启动监控...")
try:
    bili.job()
    print("✅ 本轮检查完成")
except Exception as e:
    print(f"❌ 运行错误: {e}")
    import traceback
    traceback.print_exc()

# ========== 保存状态 ==========
save_state_to_gist()
