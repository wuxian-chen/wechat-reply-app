# 微信智能回复APP

一款基于Kivy开发的Android应用，通过AI智能生成回复建议，帮助用户更高效地回复微信消息。

## 功能特性

### 核心功能
- 🔔 **消息监听** - 自动监听微信消息通知
- 💡 **智能回复** - AI生成3-5个回复建议
- 📋 **一键复制** - 点击即可复制回复内容
- 📜 **历史记录** - 保存聊天历史方便回顾

### 系统集成
- 🔄 **开机自启** - 支持开机自动启动
- 🖥️ **悬浮窗显示** - 不离开微信直接查看回复
- 🔒 **后台运行** - 支持后台持续运行

## 界面预览

### 主界面
- 女友微信名/备注设置
- 通义千问API Key配置
- 监听开关控制
- API连接测试

### 悬浮窗
- 消息内容展示
- 回复建议列表（3-5条）
- 一键复制功能
- 重新生成按钮

## 安装说明

### 方式一：使用Buildozer本地打包

#### 1. 安装依赖

**Ubuntu/Debian:**
```bash
# 安装编译工具
sudo apt update
sudo apt install -y python3 python3-pip git zip unzip openjdk-11-jdk

# 安装Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
mkdir -p ~/android-sdk/cmdline-tools
mv cmdlinetools-linux-9477386_latest.zip ~/android-sdk/cmdline-tools/
cd ~/android-sdk/cmdline-tools/
unzip commandlinetools-linux-9477386_latest.zip
mv cmdline-tools latest

# 设置环境变量
export ANDROID_SDK_ROOT=~/android-sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools
```

**macOS:**
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python3 git unzip openjdk@11
brew install --cask android-sdk
```

#### 2. 编译APK

```bash
# 克隆项目
cd ./自动化工具/微信回复APP

# 安装buildozer
pip3 install buildozer

# 编译APK（首次编译约需10-30分钟）
buildozer -v android debug

# APK输出位置
# buildozer bin/wechat_reply-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 方式二：在线打包服务

可以使用以下在线服务打包APK：

1. **Cloud Build** - https://cloud.buildozer.io/
2. **Google Colab** - 使用 notebook环境运行buildozer
3. **GitHub Actions** - 配置CI/CD自动构建

### 方式三：手动编译

如果本地有Android开发环境：

```bash
# 使用python-for-android
pip install python-for-android

# 编译
python -m buildozer android debug
```

## 权限说明

首次使用需要手动开启以下权限：

### 1. 无障碍服务权限（必须）
```
设置 → 辅助功能 → 无障碍服务 → 微信智能回复 → 开启
```
- 用于监听微信消息通知
- 获取消息发送者和内容

### 2. 悬浮窗权限（必须）
```
设置 → 应用 → 微信智能回复 → 悬浮窗 → 允许
```
- 用于显示回复建议悬浮窗

### 3. 通知权限（必须）
```
设置 → 应用 → 微信智能回复 → 通知 → 允许通知
```
- 用于接收和处理微信通知

### 4. 开机自启权限（可选）
```
设置 → 应用 → 微信智能回复 → 开机自启 → 允许
```
- 用于开机自动启动服务

## 使用教程

### 1. 基础配置

1. 打开APP，填写女友的微信名或备注
2. 输入通义千问API Key
3. 点击「测试API」验证连接
4. 开启消息监听开关

### 2. 接收回复建议

当女友发来消息时：
1. APP自动监听并识别
2. 弹出悬浮窗显示回复建议
3. 点击建议内容自动复制
4. 粘贴到微信发送

### 3. 查看历史

点击「历史记录」查看：
- 之前的聊天记录
- 已使用的回复
- 清空历史选项

## API配置

### 通义千问API

1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通通义千问服务
4. 创建API Key
5. 将API Key填入APP

### API Key说明

- 免费额度：有一定数量的免费调用额度
- 计费方式：按token数计费
- 推荐模型：qwen-turbo（快速响应）

## 项目结构

```
微信回复APP/
├── main.py                    # Kivy主程序
├── ai_reply.py                # AI回复生成模块
├── storage.py                 # 消息存储模块
├── accessibility_service.py   # 无障碍服务模块
├── android_service.py         # Android服务模块
├── buildozer.spec             # 打包配置文件
├── config.json                # 应用配置文件
├── icon.png                   # 应用图标
└── README.md                  # 使用说明
```

## 技术栈

- **UI框架**: Kivy / KivyMD
- **AI服务**: 通义千问 (Qwen Turbo)
- **打包工具**: Buildozer
- **目标平台**: Android 5.0+

## 注意事项

### ⚠️ 重要提示

1. **无障碍服务必须开启** - 这是监听微信消息的核心
2. **保持后台运行** - 可在电池优化中设为不受限制
3. **API Key安全** - 不要在公共场合泄露
4. **网络要求** - 需要保持网络连接

### 限制说明

- 只能监听通知形式的消息
- 无法直接发送消息（需手动复制粘贴）
- 部分微信版本可能不兼容

## 常见问题

### Q: 为什么收不到消息？
A: 请检查：
1. 无障碍服务是否开启
2. 通知权限是否授予
3. APP是否在后台运行
4. 网络是否正常

### Q: API调用失败？
A: 请检查：
1. API Key是否正确
2. API Key是否有效
3. 账户余额是否充足

### Q: 悬浮窗不显示？
A: 请检查：
1. 悬浮窗权限是否开启
2. 是否在白名单中
3. 屏幕叠加权限是否允许

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 支持消息监听
- 支持AI回复生成
- 支持历史记录

## 免责声明

本应用仅供学习和参考使用，请勿用于：
- 任何商业盈利目的
- 侵犯他人隐私
- 发送垃圾信息
- 其他违法违规用途

## 联系方式

如有问题或建议，请联系开发者。

---

**Made with ❤️ using Kivy**
