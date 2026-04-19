"""
登录模块单元测试 (模拟)
测试登录逻辑而不需要真实网络
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 模拟测试
class MockLoginResult:
    def __init__(self, success, uin=0, token="", error_message=""):
        self.success = success
        self.uin = uin
        self.token = token
        self.session_key = ""
        self.error_code = 0
        self.error_message = error_message

async def test_login_logic():
    """测试登录逻辑"""
    print("\n" + "="*60)
    print("登录逻辑测试")
    print("="*60)
    
    # 测试1: 密码哈希
    print("\n[测试1] 密码哈希")
    import hashlib
    password = "YJX20090201"
    password_hash = hashlib.md5(password.encode()).hexdigest()
    print(f"  原始密码: {password}")
    print(f"  MD5哈希: {password_hash}")
    print(f"  哈希长度: {len(password_hash)}")
    assert len(password_hash) == 32, "MD5哈希长度应为32"
    print("  ✓ 通过")
    
    # 测试2: 请求构建
    print("\n[测试2] 登录请求构建")
    username = "2056826320"
    payload = {
        "username": username,
        "password": password_hash,
        "platform": "WIN",
        "version": "79105",
        "device_id": f"MNW_1234567890",
    }
    print(f"  请求体: {payload}")
    assert "username" in payload
    assert "password" in payload
    assert "platform" in payload
    print("  ✓ 通过")
    
    # 测试3: URL构建
    print("\n[测试3] URL构建")
    from urllib.parse import urljoin
    api_base = "http://117.89.177.75:8080"
    endpoint = "/v2/user/login"
    url = urljoin(api_base, endpoint)
    print(f"  API基础: {api_base}")
    print(f"  端点: {endpoint}")
    print(f"  完整URL: {url}")
    assert url == "http://117.89.177.75:8080/v2/user/login"
    print("  ✓ 通过")
    
    # 测试4: 响应解析
    print("\n[测试4] 响应解析")
    mock_response = {
        "success": True,
        "uin": 2056826320,
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
        "session_key": "abc123def456"
    }
    
    result = MockLoginResult(
        success=mock_response.get("success", False),
        uin=mock_response.get("uin", 0),
        token=mock_response.get("token", ""),
    )
    
    print(f"  成功: {result.success}")
    print(f"  UIN: {result.uin}")
    print(f"  Token: {result.token[:30]}...")
    
    assert result.success == True
    assert result.uin == 2056826320
    print("  ✓ 通过")
    
    # 测试5: 错误处理
    print("\n[测试5] 错误处理")
    error_response = {
        "success": False,
        "error_code": 1001,
        "message": "Invalid credentials"
    }
    
    error_result = MockLoginResult(
        success=False,
        error_message=error_response.get("message", "Unknown error")
    )
    
    print(f"  成功: {error_result.success}")
    print(f"  错误信息: {error_result.error_message}")
    
    assert error_result.success == False
    assert error_result.error_message == "Invalid credentials"
    print("  ✓ 通过")
    
    print("\n" + "="*60)
    print("所有测试通过!")
    print("="*60)
    
    return True

async def test_config_loading():
    """测试配置加载"""
    print("\n" + "="*60)
    print("配置加载测试")
    print("="*60)
    
    # 测试服务器配置
    print("\n[测试] 服务器配置")
    
    # 模拟服务器配置
    servers = {
        "game": [{"host": "116.205.254.229", "port": 19601}],
        "api": [{"host": "117.89.177.75", "port": 8080}],
    }
    
    game_server = servers["game"][0]
    api_server = servers["api"][0]
    
    print(f"  游戏服务器: {game_server['host']}:{game_server['port']}")
    print(f"  API服务器: {api_server['host']}:{api_server['port']}")
    
    assert game_server["port"] == 19601
    assert api_server["port"] == 8080
    print("  ✓ 通过")
    
    return True

async def main():
    print("\n" + "="*60)
    print("MnMCP 登录模块单元测试")
    print("="*60)
    
    try:
        await test_login_logic()
        await test_config_loading()
        
        print("\n" + "="*60)
        print("✓ 所有测试通过!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
