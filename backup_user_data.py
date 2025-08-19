#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import datetime

def backup_user_data():
    """备份用户数据"""
    print("=== 用户数据备份工具 ===")
    
    # 检查是否存在用户数据文件
    if not os.path.exists('user_data.json'):
        print("❌ 未找到user_data.json文件")
        return False
    
    # 读取当前用户数据
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取用户数据失败: {e}")
        return False
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'user_data_backup_{timestamp}.json'
    
    # 备份数据
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 用户数据已备份到: {backup_filename}")
        
        # 显示备份统计
        user_count = len(user_data.get('user_profiles', {}))
        print(f"📊 备份统计:")
        print(f"   - 用户数量: {user_count}")
        print(f"   - 文件大小: {os.path.getsize(backup_filename)} 字节")
        
        return True
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def restore_user_data(backup_file):
    """恢复用户数据"""
    print(f"=== 恢复用户数据: {backup_file} ===")
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    try:
        # 读取备份数据
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # 恢复数据
        with open('user_data.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print("✅ 用户数据恢复成功")
        return True
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def list_backups():
    """列出所有备份文件"""
    print("=== 备份文件列表 ===")
    
    backup_files = [f for f in os.listdir('.') if f.startswith('user_data_backup_') and f.endswith('.json')]
    
    if not backup_files:
        print("❌ 未找到备份文件")
        return
    
    backup_files.sort(reverse=True)  # 按时间倒序
    
    for i, backup_file in enumerate(backup_files, 1):
        size = os.path.getsize(backup_file)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(backup_file))
        print(f"{i}. {backup_file}")
        print(f"   大小: {size} 字节")
        print(f"   时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            backup_user_data()
        elif command == "restore" and len(sys.argv) > 2:
            restore_user_data(sys.argv[2])
        elif command == "list":
            list_backups()
        else:
            print("用法:")
            print("  python backup_user_data.py backup    # 创建备份")
            print("  python backup_user_data.py list      # 列出备份")
            print("  python backup_user_data.py restore <file>  # 恢复备份")
    else:
        print("=== 用户数据备份工具 ===")
        print("用法:")
        print("  python backup_user_data.py backup    # 创建备份")
        print("  python backup_user_data.py list      # 列出备份")
        print("  python backup_user_data.py restore <file>  # 恢复备份") 