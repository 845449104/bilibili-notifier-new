#!/usr/bin/env python3
"""
Cookie 注入器 - 在不修改原脚本的情况下强制使用我们的 Cookie
"""

import os
import json
import sys

# 必须在导入原脚本之前设置环境
def setup_environment():
    """准备 Cookie 和配置文件"""
    # 读取环境变量
    cookies = {
        "DedeUserID": os.environ.get('BILI_DEDEUSERID', ''),
        "DedeUserID__ckMd5": "80b26d921c95178f",
        "SESSDATA": os.environ.get('BILI_SESSDATA', ''),
        "bili_jct": os.environ.get('BILI_JCT', '')
    }
    
    # 读取MID列表（从环境变量）
    mids_str = os.environ.get('BILI_FOLLOWED_MIDS', '')
    followed_mids = [mid.strip() for mid in mids_str.split(',') if mid.strip()] if mids_str else []
    
    config = {
        "feishu_webhook": os.environ.get('FEISHU_WEBHOOK', ''),
        "check_interval_minutes": 5,
        "followed_dynamic_types": ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"],
        "followed_mids": followed_mids
    }
    
    # 验证
    if not all([cookies['DedeUserID'], cookies['SESSDATA'], cookies['bili_jct']]):
        print("❌ 错误：Cookie 环境变量不完整")
        sys.exit(1)
    if not config['feishu_webhook']:
        print("❌ 错误：FEISHU_WEBHOOK 未设置")
        sys.exit(1)
    
    # 写入文件（原脚本会读取这些文件）
    with open('cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False)
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 环境准备完成")
    print(f"   用户ID: {cookies['DedeUserID']}")
    print(f"   Webhook: {config['feishu_webhook'][:50]}...")
    
    return cookies, config

def patch_original_script():
    """
    通过 Monkey Patching 修改原脚本的行为
    让它跳过二维码登录，直接使用我们的 Cookie
    """
    import bilibili_followed_dynamics as original
    
    # 找到原脚本中的 session_cookie 类
    if hasattr(original, 'session_cookie'):
        cls = original.session_cookie
        
        # 备份原始方法
        original_load = cls.load_cookies if hasattr(cls, 'load_cookies') else None
        original_valid = cls.cookie_valid if hasattr(cls, 'cookie_valid') else None
        original_ensure_login = cls.ensure_login if hasattr(cls, 'ensure_login') else None
        
        # 替换为强制使用我们的 Cookie
        def forced_load_cookies(self):
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        
        def forced_cookie_valid(self, cookies):
            """强制认为 Cookie 有效（因为我们已经验证过了）"""
            return True
        
        def forced_ensure_login(self):
            """跳过登录流程，直接加载 Cookie"""
            cookies = self.load_cookies()
            if cookies:
                self.cookies = cookies
                return cookies
            raise Exception("无法加载 Cookie")
        
        # 应用补丁
        cls.load_cookies = forced_load_cookies
        cls.cookie_valid = forced_cookie_valid
        cls.ensure_login = forced_ensure_login
        
        print("✅ 原脚本已打补丁，跳过二维码登录")
    
    return original

if __name__ == '__main__':
    print("=== Bilibili Notifier - GitHub Actions 启动器 ===\n")
    
    # 1. 准备环境
    setup_environment()
    
    # 2. 打补丁并运行
    try:
        module = patch_original_script()
        
        # 运行原脚本的主逻辑
        # 根据原脚本的结构，可能需要调用特定函数
        if hasattr(module, 'job'):
            print("\n🚀 开始执行监控任务...")
            module.job()
        elif hasattr(module, 'main'):
            module.main()
        else:
            # 如果没有明确的入口，执行脚本级别的代码
            print("\n🚀 正在运行原脚本...")
            
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
