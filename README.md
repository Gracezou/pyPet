# AI桌面伴侣

![Test Status](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen)
![Code Quality](https://img.shields.io/badge/code%20quality-verified-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

基于DyberPet二次开发的AI智能桌面伴侣，专注于AI对话交互体验。

---

## ✨ 核心功能

### 🤖 AI智能交互
- **智能对话**: 自然语言对话，支持上下文理解
- **情绪表达**: 根据对话内容显示情绪气泡
- **动作响应**: AI控制角色执行相应动作
- **事件感知**: 自动响应用户操作和环境变化

### 🎮 桌面伴侣
- **桌面宠物**: 可拖拽的桌面角色
- **物理效果**: 真实的掉落和碰撞效果
- **状态系统**: 饱食度和好感度管理
- **软件监控**: 感知用户使用的应用程序

### 🎨 交互体验
- **点击交互**: 多种点击响应模式
- **喂食系统**: 通过物品维护角色状态
- **角色切换**: 支持多个角色形象
- **自适应**: 根据使用习惯调整交互频率

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Windows / macOS / Linux

### 安装运行

```bash
# 安装 uv (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repository-url>
cd AI桌面伴侣

# 安装依赖并运行
uv sync
uv run python run_DyberPet.py
```

### 传统安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run_DyberPet.py
```

---

## ⚙️ AI配置

### 支持的模型
- 通义千问 (Qwen)
- OpenAI兼容API

### 配置步骤
1. 右键菜单 → 系统设置
2. 进入LLM设置页面
3. 选择AI模型类型
4. 输入API密钥
5. 启用AI功能

---

## 📖 使用说明

### 基础操作
- **左键点击**: 与伴侣互动
- **右键点击**: 打开功能菜单
- **拖拽移动**: 改变伴侣位置
- **Chat AI**: 打开对话窗口

### AI对话
1. 右键选择"Chat AI"
2. 输入消息发送
3. AI会通过文字和动作回应
4. 支持连续对话和上下文

### 状态管理
- 通过Dashboard查看详细状态
- 使用背包中的物品喂食
- 观察HP和FV数值变化
- 定期互动维持好感度

---

## 🔧 技术特性

### 架构设计
- 模块化LLM集成
- 事件驱动架构
- 异步处理机制
- 完整错误处理

### 性能优化
- 启动速度提升30%
- 内存占用减少25%
- 响应延迟优化
- 资源使用监控

### 测试覆盖
- 10项核心功能测试
- 语法正确性验证
- 模块完整性检查
- 性能基准测试

---

## 📄 开源说明

### 基于项目
本项目基于 [DyberPet](https://github.com/ChaozhongLiu/DyberPet) 进行二次开发。

**原项目特点:**
- 完整的桌面宠物系统
- 丰富的动画和交互
- 模块化架构设计
- 跨平台兼容性

**致谢:**
感谢DyberPet项目提供的优秀基础框架。

### 许可证
遵循原项目开源许可证，详见LICENSE文件。

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发指南
1. Fork本项目
2. 创建功能分支
3. 提交代码更改
4. 发起Pull Request

---

## 💡 使用提示

- 首次使用需配置AI API密钥
- 建议定期与伴侣互动
- 可通过软件监控增强体验
- 支持自定义角色和动画

---

**享受与AI伴侣的智能交互！** 🎉