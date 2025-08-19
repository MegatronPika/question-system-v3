#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
紧急数据恢复脚本

如果Railway部署导致数据丢失，这个脚本可以帮助恢复数据。
"""

import os
import json
import datetime
import requests
import subprocess

def check_railway_data():
    """检查Railway中的数据状态"""
    print("=== 检查Railway数据状态 ===")
    
    # 检查环境变量
    env_data = os.environ.get('USER_DATA_JSON')
    if env_data:
        try:
            data = json.loads(env_data)
            user_count = len(data.get('user_profiles', {}))
            print(f"✅ 环境变量中有数据: {user_count} 个用户")
            return data
        except json.JSONDecodeError:
            print("❌ 环境变量中的数据格式错误")
    
    # 检查持久化存储
    persistent_file = '/data/user_data.json'
    if os.path.exists(persistent_file):
        try:
            with open(persistent_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            user_count = len(data.get('user_profiles', {}))
            print(f"✅ 持久化存储中有数据: {user_count} 个用户")
            return data
        except Exception as e:
            print(f"❌ 读取持久化存储失败: {e}")
    
    # 检查本地文件
    local_file = 'user_data.json'
    if os.path.exists(local_file):
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            user_count = len(data.get('user_profiles', {}))
            print(f"✅ 本地文件中有数据: {user_count} 个用户")
            return data
        except Exception as e:
            print(f"❌ 读取本地文件失败: {e}")
    
    print("❌ 未找到任何数据")
    return None

def backup_current_data():
    """备份当前数据"""
    print("=== 备份当前数据 ===")
    
    data = check_railway_data()
    if not data:
        print("❌ 没有数据可以备份")
        return False
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'emergency_backup_{timestamp}.json'
    
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 紧急备份已创建: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ 创建紧急备份失败: {e}")
        return False

def restore_from_backup(backup_file):
    """从备份文件恢复数据"""
    print(f"=== 从备份恢复数据: {backup_file} ===")
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 保存到多个位置以确保安全
        success_count = 0
        
        # 保存到本地文件
        try:
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print("✅ 已保存到本地文件")
            success_count += 1
        except Exception as e:
            print(f"❌ 保存到本地文件失败: {e}")
        
        # 保存到持久化存储
        try:
            os.makedirs('/data', exist_ok=True)
            with open('/data/user_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print("✅ 已保存到持久化存储")
            success_count += 1
        except Exception as e:
            print(f"❌ 保存到持久化存储失败: {e}")
        
        # 尝试保存到环境变量
        try:
            data_json = json.dumps(data, ensure_ascii=False, default=str)
            subprocess.run([
                'railway', 'variables', 'set', 
                'USER_DATA_JSON', data_json
            ], check=True)
            print("✅ 已保存到环境变量")
            success_count += 1
        except Exception as e:
            print(f"❌ 保存到环境变量失败: {e}")
        
        if success_count > 0:
            print(f"✅ 数据恢复成功，保存到 {success_count} 个位置")
            return True
        else:
            print("❌ 数据恢复失败")
            return False
            
    except Exception as e:
        print(f"❌ 恢复数据失败: {e}")
        return False

def list_backup_files():
    """列出所有备份文件"""
    print("=== 备份文件列表 ===")
    
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('emergency_backup_') and file.endswith('.json'):
            file_path = file
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            size = os.path.getsize(file_path)
            backup_files.append((file, mtime, size))
    
    if not backup_files:
        print("❌ 未找到备份文件")
        return []
    
    backup_files.sort(key=lambda x: x[1], reverse=True)
    
    for i, (filename, mtime, size) in enumerate(backup_files, 1):
        print(f"{i}. {filename}")
        print(f"   时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   大小: {size} 字节")
        print()
    
    return backup_files

def create_test_data():
    """创建测试数据"""
    print("=== 创建测试数据 ===")
    
    test_data = {
        'users': {
            'test_user': {
                'username': 'test_user',
                'password_hash': 'test_hash',
                'answered_questions': [],
                'wrong_questions': []
            }
        },
        'user_profiles': {
            'test_user': {
                'username': 'test_user',
                'register_time': datetime.datetime.now().isoformat(),
                'last_login': datetime.datetime.now().isoformat()
            }
        },
        'wrong_questions': {
            'test_user': []
        },
        'exam_records': {
            'test_user': []
        }
    }
    
    try:
        with open('user_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2, default=str)
        
        print("✅ 测试数据已创建")
        return True
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 紧急数据恢复工具 ===")
    print()
    
    print("选择操作:")
    print("1. 检查当前数据状态")
    print("2. 创建紧急备份")
    print("3. 列出备份文件")
    print("4. 从备份恢复数据")
    print("5. 创建测试数据")
    print("6. 退出")
    
    choice = input("\n请选择 (1-6): ").strip()
    
    if choice == "1":
        data = check_railway_data()
        if data:
            print(f"\n数据统计:")
            print(f"  用户数量: {len(data.get('user_profiles', {}))}")
            print(f"  错题总数: {sum(len(wrong) for wrong in data.get('wrong_questions', {}).values())}")
            print(f"  考试记录: {sum(len(records) for records in data.get('exam_records', {}).values())}")
    elif choice == "2":
        backup_current_data()
    elif choice == "3":
        list_backup_files()
    elif choice == "4":
        backups = list_backup_files()
        if backups:
            try:
                backup_index = int(input("请输入备份文件编号: ")) - 1
                if 0 <= backup_index < len(backups):
                    backup_file = backups[backup_index][0]
                    restore_from_backup(backup_file)
                else:
                    print("❌ 无效的编号")
            except ValueError:
                print("❌ 请输入有效的数字")
    elif choice == "5":
        create_test_data()
    elif choice == "6":
        print("退出")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 