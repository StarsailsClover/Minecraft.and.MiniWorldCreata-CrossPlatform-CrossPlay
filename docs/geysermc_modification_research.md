# 改写GeyserMC可行性研究报告

研究将GeyserMC扩展为支持"MC两端 + 迷你世界四端"互通的可行性。

---

## 1. GeyserMC架构分析

### 1.1 当前架构
```
Bedrock Client → GeyserMC → Java Server
                    ↓
              协议转换层
                    ↓
Java Client ← GeyserMC ← Java Server
```

### 1.2 核心组件
- **BedrockPacketProcessor**: 处理基岩版数据包
- **JavaPacketProcessor**: 处理Java版数据包
- **Translators**: 协议转换器集合
- **Session Management**: 会话管理

---

## 2. 扩展可行性分析

### 2.1 技术可行性: ✅ 可行

**理由**:
1. GeyserMC本身就是协议桥接器，架构可扩展
2. 已支持双向协议转换（Bedrock ↔ Java）
3. 模块化设计，易于添加新的协议适配器

### 2.2 实现方案

#### 方案A: 扩展GeyserMC（推荐）
```
MiniWorld Client → MiniWorld Adapter → GeyserMC → Java Server
                         ↓
                    迷你世界协议转换
                         ↓
Bedrock Client → Bedrock Adapter → GeyserMC → Java Server
                      ↓
                 基岩版协议转换
                      ↓
Java Client ← Java Server
```

**实现步骤**:
1. 创建 `MiniWorldSession` 类（类似 BedrockSession）
2. 实现 `MiniWorldPacketProcessor` 处理器
3. 创建迷你世界协议转换器集合
4. 集成到GeyserMC的会话管理系统

#### 方案B: 独立代理层
```
MiniWorld Client → MiniWorld Proxy → GeyserMC → Java Server
Bedrock Client → GeyserMC → Java Server
Java Client → Java Server
```

**优缺点**:
- ✅ 不修改GeyserMC源码
- ❌ 增加一层转发，延迟增加

---

## 3. 技术挑战

### 3.1 协议差异

| 方面 | Minecraft | 迷你世界 | 难度 |
|------|-----------|----------|------|
| 数据包格式 | 标准格式 | 自定义 | 中 |
| 加密方式 | AES-CFB8 | AES-128-CBC | 中 |
| 压缩方式 | Zlib | 未知 | 高 |
| 实体ID | 标准 | 自定义 | 中 |
| 方块ID | 标准 | 自定义 | 高 |

### 3.2 实现难点

1. **协议逆向工程**
   - 需要完整逆向迷你世界协议
   - 包括登录、游戏状态、实体同步等

2. **ID映射表构建**
   - 方块ID映射（数千种）
   - 实体ID映射
   - 物品ID映射
   - 粒子效果映射

3. **坐标系转换**
   - 迷你世界与MC坐标系差异
   - 需要实时坐标转换

4. **功能差异处理**
   - 迷你世界特有功能（电路系统）
   - Minecraft特有功能（红石系统）
   - 需要功能屏蔽或模拟

---

## 4. 工作量评估

### 4.1 开发阶段

| 阶段 | 工作量 | 时间估计 |
|------|--------|----------|
| 协议逆向工程 | 大 | 2-4周 |
| ID映射表构建 | 大 | 2-3周 |
| GeyserMC扩展开发 | 中 | 2-3周 |
| 协议转换器实现 | 大 | 3-4周 |
| 测试与优化 | 中 | 2-3周 |
| **总计** | **很大** | **11-17周** |

### 4.2 技术难度

- **整体难度**: ⭐⭐⭐⭐⭐ (5/5)
- **协议逆向**: ⭐⭐⭐⭐⭐ (5/5)
- **GeyserMC扩展**: ⭐⭐⭐ (3/5)
- **ID映射**: ⭐⭐⭐⭐ (4/5)

---

## 5. 建议方案

### 5.1 短期方案（推荐）

**独立代理服务器**:
```
MiniWorld Client → MiniWorld Proxy → Java Server → GeyserMC → Bedrock Client
```

**优点**:
- 不修改GeyserMC
- 开发周期短（4-6周）
- 风险可控

### 5.2 长期方案

**深度集成GeyserMC**:
- Fork GeyserMC项目
- 添加迷你世界支持
- 提交PR到上游（如果被接受）

---

## 6. 结论

### 可行性: ✅ **技术上可行**

**但是**:
- 工作量很大（11-17周）
- 需要完整的协议逆向工程
- 需要构建完整的ID映射表
- 需要处理大量功能差异

### 建议

1. **第一阶段**: 完成独立代理服务器（当前项目方向）
2. **第二阶段**: 考虑深度集成GeyserMC
3. **评估标准**: 第一阶段成功后，评估是否值得投入GeyserMC扩展

### 风险

- 迷你世界协议变更可能导致大量返工
- ID映射表维护成本高
- 功能差异可能导致部分功能无法互通

---

## 7. 添加到开发计划

建议在开发计划中增加：

```markdown
### 长期规划: GeyserMC深度集成（可选）
- [ ] 评估独立代理服务器效果
- [ ] Fork GeyserMC项目
- [ ] 设计迷你世界适配器架构
- [ ] 实现MiniWorldSession
- [ ] 实现迷你世界协议转换器
- [ ] 集成ID映射表
- [ ] 测试与优化
- [ ] 考虑提交PR到GeyserMC上游
```

---

Made with ❤️ by ZCNotFound for cross-platform gaming

**研究日期**: 2026-02-26
**结论**: 技术上可行，但工作量大，建议先完成独立代理服务器
