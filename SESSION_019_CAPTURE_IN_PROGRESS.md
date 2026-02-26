# Session 019 - PC端抓包执行中

## 执行时间：2026-02-26

---

## 一、已执行操作

### ✅ 1. 找到软件安装位置
- **Wireshark**: `D:\Program Files\Wireshark\`
- **Proxifier**: `D:\Program Files (x86)\Proxifier\`
- **tshark**: `D:\Program Files\Wireshark\tshark.exe`

### ✅ 2. 启动抓包环境
- **Wireshark**: 已启动
- **抓包脚本**: `capture_cn_updated.bat` 已运行

### ✅ 3. 创建抓包分析工具
- **工具**: `tools/pc_capture/analyze_pcap.py`
- **功能**: 自动分析.pcapng文件，提取协议信息

---

## 二、你现在需要做的

### 步骤1：在Wireshark中配置抓包
1. **选择网络接口**
   - 在Wireshark中选择你的网络接口（Wi-Fi或有线网卡）

2. **设置过滤器**
   ```
   host mini1.cn or host miniworldgame.com
   ```
   或者在过滤器栏输入：
   ```
   tcp or udp
   ```

3. **开始抓包**
   - 点击蓝色鲨鱼鳍按钮开始抓包

### 步骤2：启动迷你世界国服
1. **运行游戏**
   - 如果抓包脚本没有自动启动，手动启动：
   ```
   C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\miniworldPC_CN\miniworldLauncher\iworldpc.exe
   ```

2. **执行操作**
   - 登录游戏（使用账号：2056574316）
   - 创建房间或加入房间
   - 进行游戏操作（移动、放置方块、聊天）
   - 邀请好友（如果有第二账号）
   - 退出游戏

### 步骤3：保存抓包文件
1. **停止抓包**
   - 回到Wireshark
   - 点击红色方块停止抓包

2. **保存文件**
   - 点击 `文件` -> `保存`
   - 文件名：`cn_capture.pcapng`
   - 保存位置：`C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\captures\`

### 步骤4：执行外服抓包（可选）
重复上述步骤，但启动外服版本：
```
C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\miniworldPC_Global\miniworldOverseasgame\iworldpc.exe
```
保存为：`global_capture.pcapng`

---

## 三、抓包完成后

### 运行分析工具
```bash
cd "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\pc_capture"
python analyze_pcap.py
```

**自动分析内容**：
- 总包数统计
- 唯一IP地址识别
- 通信端口识别
- 数据包大小分布
- 可能的迷你世界服务器IP

---

## 四、抓包重点

### 1. 登录阶段
- 捕获认证服务器通信
- 识别登录请求格式
- 提取Token/Session信息

### 2. 房间管理
- 创建房间请求
- 加入房间流程
- 房间列表同步

### 3. 游戏同步
- 玩家位置同步（频率、精度）
- 方块操作同步
- 聊天消息格式

### 4. 心跳包
- 保活机制
- 间隔时间
- 数据包结构

---

## 五、预期产出

### 抓包文件
```
captures/
├── cn_capture.pcapng          # 国服抓包（你正在执行）
├── global_capture.pcapng      # 外服抓包（可选）
└── analysis/
    └── PCAP_ANALYSIS_REPORT.md  # 自动生成的分析报告
```

### 关键信息
- 迷你世界服务器IP和端口
- 登录认证流程
- 数据包结构
- 加密方式（如果能识别）

---

## 六、常见问题

### Q: Wireshark没有显示数据包？
**A**: 
1. 检查是否选择了正确的网络接口
2. 尝试不使用过滤器，捕获所有流量
3. 确保游戏确实产生了网络通信

### Q: 抓包文件很大？
**A**: 
- 正常，游戏会产生大量数据
- 可以只抓包2-3分钟的关键操作
- 分析时可以使用过滤器

### Q: 无法识别协议？
**A**: 
- 迷你世界可能使用自定义协议
- 数据可能加密
- 需要结合脱壳代码分析

---

## 七、当前状态

| 任务 | 状态 | 说明 |
|------|------|------|
| Wireshark启动 | ✅ 完成 | 已启动并等待配置 |
| 游戏启动 | 🔄 等待 | 等待你启动游戏 |
| 抓包执行 | 🔄 等待 | 等待你执行操作 |
| 保存文件 | 🔄 等待 | 等待你保存抓包 |
| 分析抓包 | ⬜ 未开始 | 保存后自动分析 |

---

## 八、下一步（抓包完成后）

1. **运行分析工具**
   ```bash
   python tools/pc_capture/analyze_pcap.py
   ```

2. **查看分析报告**
   - 识别服务器IP
   - 分析通信端口
   - 提取协议特征

3. **对比国服/外服**（如果都有抓包）
   - 对比服务器地址
   - 对比登录流程
   - 对比数据包结构

4. **继续Frida脱壳分析**（如果已完成）
   - 复制DEX文件
   - 反编译分析
   - 对比抓包结果

---

**请完成抓包后告诉我，我会立即运行分析工具！**

**预计时间**：
- 抓包操作：5-10分钟
- 自动分析：1-2分钟
- 结果查看：5分钟
