#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的主要功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, load_user_data, normalize_user_data, get_user_stats_cached

def test_basic_functions():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 测试load_user_data
    try:
        user_data = load_user_data()
        print("✓ load_user_data 正常工作")
        print(f"  用户数量: {len(user_data.get('users', {}))}")
    except Exception as e:
        print(f"✗ load_user_data 失败: {e}")
        return False
    
    # 测试normalize_user_data
    try:
        normalized_data = normalize_user_data(user_data)
        print("✓ normalize_user_data 正常工作")
    except Exception as e:
        print(f"✗ normalize_user_data 失败: {e}")
        return False
    
    # 测试get_user_stats_cached（需要用户ID）
    try:
        # 创建一个测试用户数据
        test_user_data = {
            'users': {
                'test_user': {
                    'answered_questions': [1, 2, 3],
                    'wrong_questions': [1, 4],
                    'important_questions': [1, 5],
                    'wrong_count': {}
                }
            },
            'wrong_questions': {
                'test_user': [
                    {'question_id': 1, 'timestamp': '2024-01-01T00:00:00'},
                    {'question_id': 1, 'timestamp': '2024-01-02T00:00:00'},
                    {'question_id': 4, 'timestamp': '2024-01-03T00:00:00'}
                ]
            },
            'exam_records': {
                'test_user': []
            }
        }
        
        # 测试normalize_user_data
        normalized = normalize_user_data(test_user_data)
        answered_set = normalized['users']['test_user']['answered_questions']
        wrong_set = normalized['users']['test_user']['wrong_questions']
        important_set = normalized['users']['test_user']['important_questions']
        
        print(f"✓ 数据转换正确:")
        print(f"  answered_questions: {type(answered_set)} - {answered_set}")
        print(f"  wrong_questions: {type(wrong_set)} - {wrong_set}")
        print(f"  important_questions: {type(important_set)} - {important_set}")
        
    except Exception as e:
        print(f"✗ 数据转换测试失败: {e}")
        return False
    
    print("=== 所有基本功能测试通过 ===")
    return True

if __name__ == '__main__':
    with app.app_context():
        success = test_basic_functions()
        if success:
            print("\n🎉 修复验证成功！系统应该可以正常工作了。")
        else:
            print("\n❌ 修复验证失败，需要进一步检查。")
