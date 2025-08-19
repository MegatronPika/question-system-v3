#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地启动脚本
确保不影响Git代码，数据文件不会被提交到Git
"""

import os
import sys
import subprocess
import json
import datetime

def check_dependencies():
    """检查依赖"""
    print("=== 检查依赖 ===")
    
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("❌ Flask 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=True)
        print("✅ Flask 安装完成")
    
    try:
        import werkzeug
        print("✅ Werkzeug 已安装")
    except ImportError:
        print("❌ Werkzeug 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "werkzeug"], check=True)
        print("✅ Werkzeug 安装完成")

def check_data_files():
    """检查数据文件"""
    print("\n=== 检查数据文件 ===")
    
    # 检查题库文件
    if os.path.exists('full_questions.json'):
        with open('full_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        question_count = len(data.get('questions', []))
        print(f"✅ 题库文件存在，共 {question_count} 道题目")
    else:
        print("❌ 题库文件不存在")
        return False
    
    # 检查用户数据文件
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        user_count = len(data.get('user_profiles', {}))
        print(f"✅ 用户数据文件存在，共 {user_count} 个用户")
    else:
        print("ℹ️ 用户数据文件不存在，将自动创建")
    
    return True

def setup_local_environment():
    """设置本地环境"""
    print("\n=== 设置本地环境 ===")
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['PORT'] = '8080'
    
    # 确保数据目录存在
    os.makedirs('.', exist_ok=True)
    
    print("✅ 本地环境设置完成")

def backup_user_data():
    """备份用户数据"""
    if os.path.exists('user_data.json'):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'user_data_backup_{timestamp}.json'
        
        try:
            with open('user_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 用户数据已备份到: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    return True

def start_server():
    """启动服务器"""
    print("\n=== 启动服务器 ===")
    
    # 尝试不同的端口
    ports = [8080, 8081, 8082, 8083, 8084]
    available_port = None
    
    import socket
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:
            available_port = port
            break
    
    if available_port is None:
        print("❌ 所有端口都被占用")
        print("请停止其他服务或手动指定端口")
        return False
    
    print(f"✅ 端口 {available_port} 可用")
    print(f"\n🚀 启动服务器...")
    print(f"访问地址: http://localhost:{available_port}")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=available_port)
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== 金融业数字化转型技能大赛题库系统 - 本地启动 ===")
    print()
    
    # 检查依赖
    check_dependencies()
    
    # 检查数据文件
    if not check_data_files():
        print("❌ 数据文件检查失败，请确保题库文件存在")
        return
    
    # 设置本地环境
    setup_local_environment()
    
    # 备份用户数据
    backup_user_data()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 