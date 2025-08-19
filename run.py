#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def check_dependencies():
    """检查依赖"""
    try:
        import flask
        print("✓ Flask 已安装")
    except ImportError:
        print("✗ Flask 未安装，正在安装...")
        os.system("pip install -r requirements.txt")

def check_data_files():
    """检查数据文件"""
    if not os.path.exists('full_questions.json'):
        print("✗ 题库文件不存在，请确保 full_questions.json 文件存在")
        return False
    print("✓ 题库文件存在")
    return True

def main():
    print("=== 金融业数字化转型技能大赛题库系统 ===")
    
    # 检查依赖
    check_dependencies()
    
    # 检查数据文件
    if not check_data_files():
        sys.exit(1)
    
    print("\n启动服务器...")
    print("访问地址: http://localhost:8080")
    print("按 Ctrl+C 停止服务器")
    
    # 启动Flask应用
    from app import app
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main() 