#!/usr/bin/env python3
"""
登录认证处理器
处理Minecraft和迷你世界之间的登录转换
"""

import json
import hashlib
import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MinecraftAccount:
    """Minecraft账户信息"""
    username: str
    uuid: str
    access_token: str = ""
    
@dataclass
class MiniWorldAccount:
    """迷你世界账户信息"""
    account_id: str  # 迷你号
    token: str
    session_key: str = ""
    nickname: str = ""

class AccountMapper:
    """账户映射器"""
    
    def __init__(self):
        # 账户映射表 (Minecraft UUID -> 迷你号)
        self.mappings: Dict[str, str] = {}
        # 加载已有映射
        self._load_mappings()
    
    def _load_mappings(self):
        """从文件加载映射"""
        try:
            import os
            mapping_file = os.path.expanduser("~/.mnmcp/account_mappings.json")
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r') as f:
                    self.mappings = json.load(f)
                logger.info(f"[+] 加载了 {len(self.mappings)} 个账户映射")
        except Exception as e:
            logger.warning(f"[!] 加载账户映射失败: {e}")
    
    def _save_mappings(self):
        """保存映射到文件"""
        try:
            import os
            mapping_dir = os.path.expanduser("~/.mnmcp")
            os.makedirs(mapping_dir, exist_ok=True)
            mapping_file = os.path.join(mapping_dir, "account_mappings.json")
            with open(mapping_file, 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            logger.warning(f"[!] 保存账户映射失败: {e}")
    
    def get_miniworld_account(self, mc_uuid: str) -> Optional[str]:
        """获取对应的迷你号"""
        return self.mappings.get(mc_uuid)
    
    def create_mapping(self, mc_uuid: str, mnw_account_id: str):
        """创建账户映射"""
        self.mappings[mc_uuid] = mnw_account_id
        self._save_mappings()
        logger.info(f"[+] 创建账户映射: {mc_uuid} -> {mnw_account_id}")

class LoginHandler:
    """登录处理器"""
    
    def __init__(self):
        self.account_mapper = AccountMapper()
        self.active_sessions: Dict[str, MiniWorldAccount] = {}
    
    def convert_mc_to_mnw_login(self, mc_account: MinecraftAccount) -> Dict:
        """
        转换Minecraft登录请求为迷你世界格式
        
        Args:
            mc_account: Minecraft账户信息
            
        Returns:
            迷你世界登录请求JSON
        """
        # 查找已有的迷你号映射
        mnw_account_id = self.account_mapper.get_miniworld_account(mc_account.uuid)
        
        if not mnw_account_id:
            # 如果没有映射，生成一个基于UUID的虚拟迷你号
            # 实际使用时应该让用户输入真实迷你号
            mnw_account_id = self._generate_virtual_account(mc_account.uuid)
            self.account_mapper.create_mapping(mc_account.uuid, mnw_account_id)
            logger.info(f"[*] 为 {mc_account.username} 生成虚拟迷你号: {mnw_account_id}")
        
        # 构建迷你世界登录请求
        login_request = {
            "cmd": "login",
            "account": mnw_account_id,
            "password": "",  # 需要用户输入
            "version": "1.53.1",
            "platform": "pc",
            "channel": "110",
            "device_id": self._generate_device_id(mc_account.uuid),
            "timestamp": int(__import__('time').time()),
            "sign": ""  # 需要计算签名
        }
        
        logger.info(f"[*] 转换登录请求: {mc_account.username} -> {mnw_account_id}")
        return login_request
    
    def convert_mnw_to_mc_login_response(self, mnw_response: Dict) -> Dict:
        """
        转换迷你世界登录响应为Minecraft格式
        
        Args:
            mnw_response: 迷你世界登录响应
            
        Returns:
            Minecraft登录响应JSON
        """
        # 提取迷你世界Token
        token = mnw_response.get("token", "")
        session_key = mnw_response.get("session_key", "")
        nickname = mnw_response.get("nickname", "Player")
        
        # 构建Minecraft登录响应
        mc_response = {
            "name": nickname,
            "id": mnw_response.get("account_id", ""),
            "properties": [
                {
                    "name": "mnw_token",
                    "value": token
                },
                {
                    "name": "mnw_session_key",
                    "value": session_key
                }
            ]
        }
        
        logger.info(f"[*] 转换登录响应: {nickname}")
        return mc_response
    
    def _generate_virtual_account(self, mc_uuid: str) -> str:
        """基于Minecraft UUID生成虚拟迷你号"""
        # 使用UUID的前8位作为基础
        uuid_hash = hashlib.md5(mc_uuid.encode()).hexdigest()
        # 生成9位数字（迷你号格式）
        account_id = str(int(uuid_hash[:8], 16) % 900000000 + 100000000)
        return account_id
    
    def _generate_device_id(self, mc_uuid: str) -> str:
        """生成设备ID"""
        uuid_hash = hashlib.md5(f"device_{mc_uuid}".encode()).hexdigest()
        return uuid_hash[:16]
    
    def handle_login_error(self, error_code: int, error_msg: str) -> Dict:
        """处理登录错误"""
        error_responses = {
            1001: {"error": "账号不存在", "message": "请检查迷你号是否正确"},
            1002: {"error": "密码错误", "message": "请检查密码"},
            1003: {"error": "账号被封禁", "message": "账号已被封禁"},
            1004: {"error": "版本过低", "message": "请更新游戏版本"},
            1005: {"error": "服务器维护", "message": "服务器维护中"},
        }
        
        error_info = error_responses.get(error_code, {
            "error": "未知错误",
            "message": error_msg
        })
        
        logger.error(f"[-] 登录错误 [{error_code}]: {error_info['error']}")
        return error_info

# 测试代码
if __name__ == "__main__":
    handler = LoginHandler()
    
    # 测试Minecraft账户
    mc_account = MinecraftAccount(
        username="TestPlayer",
        uuid="12345678-1234-1234-1234-123456789012"
    )
    
    # 转换登录请求
    login_request = handler.convert_mc_to_mnw_login(mc_account)
    print(f"登录请求: {json.dumps(login_request, indent=2, ensure_ascii=False)}")
    
    # 测试登录响应转换
    mnw_response = {
        "account_id": "2056574316",
        "token": "test_token_12345",
        "session_key": "test_session_key",
        "nickname": "测试玩家"
    }
    
    mc_response = handler.convert_mnw_to_mc_login_response(mnw_response)
    print(f"\n登录响应: {json.dumps(mc_response, indent=2, ensure_ascii=False)}")
