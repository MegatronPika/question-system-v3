#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Railway持久化存储解决方案

由于Railway的文件系统是临时的，我们需要使用以下策略来保持数据持久化：

1. 使用Railway的持久化卷（Persistent Volume）
2. 使用环境变量存储数据
3. 使用外部数据库服务
4. 定期备份到外部存储

这个脚本提供了多种数据持久化方案。
"""

import os
import json
import datetime
import subprocess
import requests
from pathlib import Path

class RailwayDataManager:
    def __init__(self):
        self.is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
        self.data_dir = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', '/data')
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_persistent_file_path(self, filename):
        """获取持久化文件路径"""
        return os.path.join(self.data_dir, filename)
    
    def save_data_persistent(self, data, filename='user_data.json'):
        """保存数据到持久化存储"""
        file_path = self.get_persistent_file_path(filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # 创建备份
            self.create_backup(data, filename)
            
            print(f"✅ 数据已保存到持久化存储: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 保存到持久化存储失败: {e}")
            return False
    
    def load_data_persistent(self, filename='user_data.json'):
        """从持久化存储加载数据"""
        file_path = self.get_persistent_file_path(filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 从持久化存储加载失败: {e}")
        
        # 如果持久化存储不存在，尝试从环境变量加载
        return self.load_data_from_env()
    
    def load_data_from_env(self):
        """从环境变量加载数据"""
        env_data = os.environ.get('USER_DATA_JSON')
        if env_data:
            try:
                return json.loads(env_data)
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in USER_DATA_JSON environment variable")
        
        return {
            'users': {},
            'user_profiles': {},
            'wrong_questions': {},
            'exam_records': {}
        }
    
    def save_data_to_env(self, data):
        """将数据保存到环境变量（通过Railway CLI）"""
        if not self.is_railway:
            print("⚠️ 不在Railway环境中，跳过环境变量保存")
            return False
        
        try:
            # 将数据转换为JSON字符串
            data_json = json.dumps(data, ensure_ascii=False, default=str)
            
            # 使用Railway CLI设置环境变量
            subprocess.run([
                'railway', 'variables', 'set', 
                'USER_DATA_JSON', data_json
            ], check=True)
            
            print("✅ 数据已保存到环境变量")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 保存到环境变量失败: {e}")
            return False
    
    def create_backup(self, data, filename='user_data.json'):
        """创建数据备份"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{filename.replace('.json', '')}_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ 备份已创建: {backup_path}")
            
            # 清理旧备份（保留最近10个）
            self.cleanup_old_backups()
            
            return True
        except Exception as e:
            print(f"❌ 创建备份失败: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count=10):
        """清理旧备份文件"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.json') and 'backup' in file:
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的备份
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                print(f"🗑️ 删除旧备份: {file_path}")
                
        except Exception as e:
            print(f"❌ 清理旧备份失败: {e}")
    
    def restore_from_backup(self, backup_filename):
        """从备份恢复数据"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 保存到持久化存储
            return self.save_data_persistent(data)
        except Exception as e:
            print(f"❌ 从备份恢复失败: {e}")
            return False
    
    def list_backups(self):
        """列出所有备份"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.json') and 'backup' in file:
                    file_path = os.path.join(self.backup_dir, file)
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    size = os.path.getsize(file_path)
                    backup_files.append((file, mtime, size))
            
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            print("=== 备份文件列表 ===")
            for filename, mtime, size in backup_files:
                print(f"{filename}")
                print(f"  时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  大小: {size} 字节")
                print()
            
            return backup_files
        except Exception as e:
            print(f"❌ 列出备份失败: {e}")
            return []

def setup_railway_persistent_volume():
    """设置Railway持久化卷"""
    print("=== 设置Railway持久化卷 ===")
    
    # 检查是否在Railway环境中
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        print("⚠️ 不在Railway环境中")
        return False
    
    try:
        # 创建持久化目录
        data_dir = '/data'
        os.makedirs(data_dir, exist_ok=True)
        
        # 设置权限
        os.chmod(data_dir, 0o755)
        
        print(f"✅ 持久化卷已设置: {data_dir}")
        return True
    except Exception as e:
        print(f"❌ 设置持久化卷失败: {e}")
        return False

def main():
    """主函数"""
    print("=== Railway数据持久化管理工具 ===")
    
    manager = RailwayDataManager()
    
    print("\n选择操作:")
    print("1. 设置持久化卷")
    print("2. 创建数据备份")
    print("3. 列出备份文件")
    print("4. 从备份恢复")
    print("5. 测试数据持久化")
    print("6. 退出")
    
    choice = input("\n请选择 (1-6): ").strip()
    
    if choice == "1":
        setup_railway_persistent_volume()
    elif choice == "2":
        # 加载当前数据并创建备份
        data = manager.load_data_persistent()
        manager.create_backup(data)
    elif choice == "3":
        manager.list_backups()
    elif choice == "4":
        backups = manager.list_backups()
        if backups:
            backup_name = input("请输入要恢复的备份文件名: ").strip()
            manager.restore_from_backup(backup_name)
    elif choice == "5":
        # 测试数据持久化
        test_data = {
            'test_time': datetime.datetime.now().isoformat(),
            'test_data': {'key': 'value'}
        }
        manager.save_data_persistent(test_data, 'test_data.json')
        loaded_data = manager.load_data_persistent('test_data.json')
        print(f"测试结果: {loaded_data == test_data}")
    elif choice == "6":
        print("退出")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 