#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import datetime
import subprocess
import requests

def check_railway_cli():
    """检查Railway CLI是否安装"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI 已安装")
            return True
        else:
            print("❌ Railway CLI 未安装或未配置")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI 未安装")
        return False

def install_railway_cli():
    """安装Railway CLI"""
    print("=== 安装Railway CLI ===")
    
    # 检查操作系统
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("在macOS上安装Railway CLI...")
        try:
            subprocess.run(['brew', 'install', 'railway'], check=True)
            print("✅ Railway CLI 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ 通过Homebrew安装失败")
            print("请手动安装: https://docs.railway.app/develop/cli")
            return False
    elif system == "linux":
        print("在Linux上安装Railway CLI...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://railway.app/install.sh', '|', 'sh'], check=True)
            print("✅ Railway CLI 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ 安装失败")
            print("请手动安装: https://docs.railway.app/develop/cli")
            return False
    else:
        print("❌ 不支持的操作系统")
        print("请手动安装: https://docs.railway.app/develop/cli")
        return False

def backup_via_railway_cli():
    """通过Railway CLI备份数据"""
    print("=== 通过Railway CLI备份数据 ===")
    
    if not check_railway_cli():
        if not install_railway_cli():
            return False
    
    try:
        # 登录Railway
        print("正在登录Railway...")
        subprocess.run(['railway', 'login'], check=True)
        
        # 列出项目
        print("正在获取项目列表...")
        result = subprocess.run(['railway', 'projects'], capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # 下载user_data.json
        print("正在下载user_data.json...")
        subprocess.run(['railway', 'download', 'user_data.json'], check=True)
        
        if os.path.exists('user_data.json'):
            # 创建备份
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'railway_user_data_backup_{timestamp}.json'
            
            with open('user_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已备份到: {backup_filename}")
            
            # 显示统计信息
            user_count = len(data.get('user_profiles', {}))
            print(f"📊 备份统计:")
            print(f"   - 用户数量: {user_count}")
            print(f"   - 文件大小: {os.path.getsize(backup_filename)} 字节")
            
            return True
        else:
            print("❌ 未找到user_data.json文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Railway CLI 操作失败: {e}")
        return False

def backup_via_api():
    """通过API备份数据（如果应用支持）"""
    print("=== 通过API备份数据 ===")
    
    # 这里需要您的Railway应用URL
    app_url = input("请输入您的Railway应用URL (例如: https://your-app.railway.app): ").strip()
    
    if not app_url:
        print("❌ 未提供应用URL")
        return False
    
    try:
        # 尝试通过API获取数据
        response = requests.get(f"{app_url}/api/backup", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 创建备份
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'api_user_data_backup_{timestamp}.json'
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 数据已备份到: {backup_filename}")
            return True
        else:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def manual_backup_guide():
    """手动备份指南"""
    print("=== 手动备份指南 ===")
    print()
    print("如果自动备份失败，请按以下步骤手动备份：")
    print()
    print("1. 登录Railway控制台: https://railway.app")
    print("2. 选择您的项目")
    print("3. 进入 'Deployments' 标签")
    print("4. 点击最新的部署")
    print("5. 在 'Files' 部分找到 user_data.json")
    print("6. 点击下载按钮保存文件")
    print("7. 将文件重命名为: user_data_backup_YYYYMMDD_HHMMSS.json")
    print()
    print("或者通过Railway CLI:")
    print("1. 安装Railway CLI: npm install -g @railway/cli")
    print("2. 登录: railway login")
    print("3. 下载文件: railway download user_data.json")
    print()

def main():
    print("=== Railway数据备份工具 ===")
    print()
    
    print("选择备份方式:")
    print("1. Railway CLI自动备份")
    print("2. API备份（如果支持）")
    print("3. 显示手动备份指南")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == "1":
        backup_via_railway_cli()
    elif choice == "2":
        backup_via_api()
    elif choice == "3":
        manual_backup_guide()
    elif choice == "4":
        print("退出备份工具")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 