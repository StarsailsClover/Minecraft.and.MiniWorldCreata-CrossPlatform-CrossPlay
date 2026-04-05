#!/usr/bin/env python3
"""
登录和房间功能测试
"""

import sys
sys.path.insert(0, '.')

from src.auth import MiniWorldLogin, LoginResult
from src.room import RoomManager, RoomMode, RoomPermission


def test_login_structure():
    """测试登录结构"""
    print("\n=== Testing Login Structure ===")
    
    login = MiniWorldLogin()
    
    print(f"✓ Login API Base: {login.API_BASE}")
    print(f"✓ Endpoints: {list(login.ENDPOINTS.keys())}")
    
    # 测试设备 ID 生成
    device_id = login._generate_device_id()
    print(f"✓ Device ID: {device_id}")
    
    print("✓ Login structure test passed")


def test_room_manager_structure():
    """测试房间管理器结构"""
    print("\n=== Testing Room Manager Structure ===")
    
    # 模拟登录后的房间管理器
    manager = RoomManager(uin=123456, token="test_token")
    
    print(f"✓ Room API Base: {manager.API_BASE}")
    print(f"✓ Endpoints: {list(manager.ENDPOINTS.keys())}")
    print(f"✓ UIN: {manager.uin}")
    
    # 测试房间模式
    print(f"✓ Room Modes: SURVIVAL={RoomMode.SURVIVAL}, CREATIVE={RoomMode.CREATIVE}")
    print(f"✓ Permissions: PUBLIC={RoomPermission.PUBLIC}, PRIVATE={RoomPermission.PRIVATE}")
    
    print("✓ Room manager structure test passed")


def test_login_result():
    """测试登录结果"""
    print("\n=== Testing Login Result ===")
    
    # 成功结果
    success_result = LoginResult(
        success=True,
        uin=123456,
        token="test_token_123",
        session_key="test_session_key"
    )
    print(f"✓ Success result: UIN={success_result.uin}")
    
    # 失败结果
    fail_result = LoginResult(
        success=False,
        error_message="Invalid password"
    )
    print(f"✓ Fail result: {fail_result.error_message}")
    
    print("✓ Login result test passed")


def main():
    """主函数"""
    print("=" * 50)
    print("Login & Room Test")
    print("=" * 50)
    
    try:
        test_login_structure()
        test_room_manager_structure()
        test_login_result()
        
        print("\n" + "=" * 50)
        print("All login & room tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
