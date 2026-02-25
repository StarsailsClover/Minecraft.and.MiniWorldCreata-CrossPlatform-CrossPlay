# 逆向工程工具集

本目录包含用于分析 Minecraft 和迷你世界协议的所有工具。

## 工具清单

### 1. APK反编译工具
- **apktool** (v2.9.3) - APK反编译与重打包
  - 使用: `apktool d app.apk`
  - 文档: https://ibotpeaches.github.io/Apktool/

### 2. Java反编译器
- **jadx** (v1.4.7) - 高级Java反编译器
  - GUI: `jadx\bin\jadx-gui.bat`
  - CLI: `jadx\bin\jadx.bat`
  - 文档: https://github.com/skylot/jadx

### 3. 动态分析工具
- **frida-server** (v16.1.11) - Android动态插桩
  - 架构: android-arm64
  - 需要root设备或模拟器
  - 文档: https://frida.re/

### 4. Python环境
- **pip** (v26.0.1) - Python包管理器
- **requirements.txt** - 依赖包列表

## 环境设置

运行以下命令设置环境:
```batch
setup_env.bat
```

这将设置:
- PYTHONPATH 包含 python_libs
- PATH 包含 Scripts

## 安装Python依赖

```batch
setup_env.bat
pip install -r requirements.txt
```

## 使用示例

### 反编译APK
```batch
apktool d app.apk -o output_folder
```

### 使用jadx GUI查看代码
```batch
jadx\bin\jadx-gui.bat app.apk
```

### 启动frida-server (需要ADB)
```batch
adb push frida-server.xz /data/local/tmp/
adb shell "cd /data/local/tmp && unxz frida-server.xz && chmod +x frida-server"
adb shell "/data/local/tmp/frida-server &"
```

## 目录结构
```
tools/
├── apktool.bat          # APK工具脚本
├── apktool.jar          # APK工具主程序
├── jadx/                # Java反编译器
│   ├── bin/
│   ├── lib/
│   └── ...
├── frida-server.xz      # Frida服务端
├── python_libs/         # Python库
├── requirements.txt     # Python依赖
├── setup_env.bat        # 环境设置脚本
└── README.md           # 本文件
```

---
Made with ❤️ by ZCNotFound for cross-platform gaming
