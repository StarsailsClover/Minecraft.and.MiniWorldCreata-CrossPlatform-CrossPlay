#!/usr/bin/env python3
"""
协议模块测试
测试登录、坐标、方块转换功能
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol import LoginHandler, CoordinateConverter, BlockMapper, Vector3

def test_login_handler():
    """测试登录处理器"""
    print("\n[*] 测试登录处理器...")
    
    handler = LoginHandler()
    
    # 测试Minecraft账户
    from protocol.login_handler import MinecraftAccount
    mc_account = MinecraftAccount(
        username="TestPlayer",
        uuid="12345678-1234-1234-1234-123456789012"
    )
    
    # 转换登录请求
    login_request = handler.convert_mc_to_mnw_login(mc_account)
    
    assert login_request["cmd"] == "login"
    assert "account" in login_request
    assert "version" in login_request
    
    print(f"  [+] 登录请求转换成功")
    print(f"      账户: {login_request['account']}")
    print(f"      版本: {login_request['version']}")
    
    return True

def test_coordinate_converter():
    """测试坐标转换器"""
    print("\n[*] 测试坐标转换器...")
    
    converter = CoordinateConverter()
    
    # 测试坐标转换
    mc_pos = Vector3(100.5, 64.0, -200.3)
    mnw_pos = converter.mc_to_mnw_position(mc_pos)
    
    # 反向转换
    mc_pos_back = converter.mnw_to_mc_position(mnw_pos)
    
    # 验证精度
    tolerance = 0.001
    assert abs(mc_pos_back.x - mc_pos.x) < tolerance
    assert abs(mc_pos_back.y - mc_pos.y) < tolerance
    assert abs(mc_pos_back.z - mc_pos.z) < tolerance
    
    print(f"  [+] 坐标转换成功")
    print(f"      MC: ({mc_pos.x}, {mc_pos.y}, {mc_pos.z})")
    print(f"      MNW: ({mnw_pos.x}, {mnw_pos.y}, {mnw_pos.z})")
    print(f"      反向: ({mc_pos_back.x}, {mc_pos_back.y}, {mc_pos_back.z})")
    
    return True

def test_block_mapper():
    """测试方块映射器"""
    print("\n[*] 测试方块映射器...")
    
    mapper = BlockMapper()
    
    # 测试已知方块
    test_cases = [
        (1, 0),   # stone
        (2, 0),   # grass
        (3, 0),   # dirt
    ]
    
    for mc_id, mc_meta in test_cases:
        mnw_id, mnw_meta = mapper.mc_to_mnw_block(mc_id, mc_meta)
        print(f"  [+] MC {mc_id}:{mc_meta} -> MNW {mnw_id}:{mnw_meta}")
    
    # 测试反向映射
    for mnw_id, mnw_meta in [(1, 0), (2, 0)]:
        mc_id, mc_meta = mapper.mnw_to_mc_block(mnw_id, mnw_meta)
        print(f"  [+] MNW {mnw_id}:{mnw_meta} -> MC {mc_id}:{mc_meta}")
    
    return True

def test_protocol_translator():
    """测试协议翻译器"""
    print("\n[*] 测试协议翻译器...")
    
    from core.protocol_translator import ProtocolTranslator, MINIWORLD_SERVERS
    
    translator = ProtocolTranslator()
    
    # 验证服务器配置
    assert "auth" in MINIWORLD_SERVERS
    assert "game_servers" in MINIWORLD_SERVERS
    assert len(MINIWORLD_SERVERS["game_servers"]) > 0
    
    print(f"  [+] 服务器配置正确")
    print(f"      认证服务器: {MINIWORLD_SERVERS['auth']['host']}")
    print(f"      游戏服务器数: {len(MINIWORLD_SERVERS['game_servers'])}")
    
    # 测试服务器选择
    server = translator.select_game_server()
    assert "ip" in server
    assert "provider" in server
    
    print(f"  [+] 服务器选择成功: {server['ip']} ({server['provider']})")
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("协议模块测试")
    print("=" * 60)
    
    tests = [
        ("登录处理器", test_login_handler),
        ("坐标转换器", test_coordinate_converter),
        ("方块映射器", test_block_mapper),
        ("协议翻译器", test_protocol_translator),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {name} 测试通过")
            else:
                failed += 1
                print(f"  ❌ {name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"  ❌ {name} 测试错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
