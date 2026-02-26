#!/usr/bin/env python3
"""
运行时获取MiniWorld方块ID的Frida脚本生成器
由于DEX源码中没有找到静态定义的方块ID，需要在运行时hook
"""

FRIDA_SCRIPT = '''
// Frida script to extract MiniWorld block IDs at runtime
// Run with: frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause

console.log("[*] MiniWorld Block ID Extractor");
console.log("[*] Waiting for block-related functions...");

// Common patterns for block ID functions in Unity games
var moduleNames = ["libunity.so", "libil2cpp.so", "libmain.so"];

function findBlockFunctions() {
    var found = [];
    
    moduleNames.forEach(function(name) {
        try {
            var module = Process.findModuleByName(name);
            if (module) {
                console.log("[+] Found module: " + name + " at " + module.base);
                
                // Search for common block function patterns
                var patterns = [
                    "getBlockId", "GetBlockId", "get_BlockId",
                    "setBlock", "SetBlock", "placeBlock",
                    "Block::getId", "Block::GetId",
                    "Terrain::get", "World::getBlock"
                ];
                
                patterns.forEach(function(p) {
                    try {
                        var exports = Module.enumerateExports(name);
                        exports.forEach(function(exp) {
                            if (exp.name && exp.name.toLowerCase().includes(p.toLowerCase())) {
                                console.log("  [+] Found: " + exp.name + " at " + exp.address);
                                found.push({name: exp.name, address: exp.address});
                            }
                        });
                    } catch(e) {}
                });
            }
        } catch(e) {}
    });
    
    return found;
}

// Hook found functions
function hookBlockFunctions(functions) {
    functions.forEach(function(func) {
        try {
            Interceptor.attach(func.address, {
                onEnter: function(args) {
                    console.log("[*] " + func.name + " called");
                    console.log("    arg0: " + args[0]);
                    console.log("    arg1: " + args[1]);
                    console.log("    arg2: " + args[2]);
                },
                onLeave: function(retval) {
                    console.log("    returned: " + retval);
                }
            });
            console.log("[+] Hooked: " + func.name);
        } catch(e) {
            console.log("[-] Failed to hook " + func.name + ": " + e);
        }
    });
}

// Main
setTimeout(function() {
    var functions = findBlockFunctions();
    console.log("[*] Found " + functions.length + " potential block functions");
    hookBlockFunctions(functions);
}, 1000);

// Alternative: Hook JNI calls for block operations
Java.perform(function() {
    console.log("[*] Java runtime ready");
    
    // Look for block-related Java classes
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.toLowerCase().includes('block') || 
                className.toLowerCase().includes('terrain') ||
                className.toLowerCase().includes('world')) {
                console.log("[Class] " + className);
            }
        },
        onComplete: function() {
            console.log("[*] Class enumeration complete");
        }
    });
});
'''

# Alternative: Packet capture approach
PACKET_CAPTURE_GUIDE = '''
## 通过网络抓包获取方块ID

由于DEX源码中没有找到静态方块ID定义，可以通过以下方法获取：

### 方法1: WebSocket抓包分析
1. 启动MiniWorld并登录
2. 使用Wireshark或mitmproxy捕获WebSocket流量
3. 在游戏中放置不同方块
4. 分析数据包中的方块ID字段

### 方法2: Frida运行时Hook
1. 使用上面生成的Frida脚本
2. 运行: frida -U -f com.minitech.miniworld -l block_id_hook.js
3. 在游戏中操作方块
4. 观察hook输出的ID值

### 方法3: 内存搜索
1. 使用GameGuardian或Cheat Engine
2. 搜索已知的方块数量或特征值
3. 定位方块ID数组在内存中的位置

### 方法4: 资源文件分析
检查APK中的以下文件：
- assets/blocks.json
- assets/data/blocks.dat
- res/raw/blocks_config
'''

def generate_frida_script():
    """生成Frida脚本文件"""
    output_path = r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\block_id_hook.js"
    with open(output_path, 'w') as f:
        f.write(FRIDA_SCRIPT)
    print(f"[+] Frida script generated: {output_path}")
    return output_path

def print_guide():
    """打印获取方块ID的指南"""
    print(PACKET_CAPTURE_GUIDE)

def main():
    print("="*60)
    print("MiniWorld Block ID Runtime Extractor")
    print("="*60)
    print()
    
    print("[*] Generating Frida script...")
    script_path = generate_frida_script()
    
    print()
    print("[*] Usage instructions:")
    print("   1. Install Frida: pip install frida-tools")
    print("   2. Connect Android device with USB debugging")
    print("   3. Run: frida -U -f com.minitech.miniworld -l block_id_hook.js")
    print()
    
    print("[*] Alternative methods:")
    print_guide()

if __name__ == "__main__":
    main()