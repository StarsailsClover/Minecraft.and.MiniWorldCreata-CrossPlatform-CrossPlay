"""
实时登录测试
使用真实账号测试登录流程
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth.login import MiniWorldLogin, login_miniworld

# 测试账号
TEST_ACCOUNTS = [
    {"username": "2056826320", "password": "YJX20090201"},
    {"username": "1234567890", "password": "TestPass123"},
]

async def test_login(account):
    """测试单个账号登录"""
    print(f"\n{'='*60}")
    print(f"测试登录: {account['username']}")
    print('='*60)
    
    try:
        result = await login_miniworld(
            account['username'],
            account['password']
        )
        
        if result:
            print(f"\n登录结果:")
            print(f"  成功: {result.success}")
            print(f"  UIN: {result.uin}")
            print(f"  Token: {result.token[:30]}..." if result.token else "  Token: None")
            print(f"  Session Key: {result.session_key[:30]}..." if result.session_key else "  Session Key: None")
            print(f"  错误码: {result.error_code}")
            print(f"  错误信息: {result.error_message}")
            
            return result.success
        else:
            print("  登录返回 None")
            return False
            
    except Exception as e:
        print(f"  登录异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "="*60)
    print("MnMCP 实时登录测试")
    print("="*60)
    
    results = []
    for account in TEST_ACCOUNTS:
        success = await test_login(account)
        results.append((account['username'], success))
    
    # 总结
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for username, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {username}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    return passed == total

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
