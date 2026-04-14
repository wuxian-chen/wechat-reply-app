[app]

# 应用标题
title = 微信智能回复

# 应用包名
package.name = wechat_reply

# 应用ID
package.domain = com.smartreply

# 应用版本
version = 1.0.0

# 源码目录
source.dir = .

# 主入口文件
source.include_exts = py,png,jpg,kv,atlas,json

# 源文件模式
source.mode = python

# 应用图标
icon.filename = icon.png

# 启动方向
orientation = portrait

# 是否全屏
fullscreen = 0

# Android API版本
android.minapi = 21
android.api = 29

# 支持的架构
android.archs = arm64-v8a, armeabi-v7a

# AndroidManifest.xml配置
androidManifestContentRequests = 
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.ACCESS_NOTIFICATION_POLICY"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    
    <!-- 无障碍服务 -->
    <service android:name="WechatAccessibilityService"
        android:exported="false"
        android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
        <intent-filter>
            <action android:name="android.accessibilityservice.AccessibilityService"/>
        </intent-filter>
        <meta-data
            android:name="android.accessibilityservice"
            android:resource="@xml/accessibility_service_config"/>
    </service>
    
    <!-- 开机启动接收器 -->
    <receiver android:name="BootReceiver"
        android:enabled="true"
        android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED"/>
            <action android:name="android.intent.action.QUICKBOOT_POWERON"/>
        </intent-filter>
    </receiver>

# 需求依赖
requirements = python3,kivy==2.1.0,https://github.com/kivymd/KivyMD/archive/master.zip,android,pyjnius,urllib3

# 日志级别
log_level = 2

# 是否禁用检查
warn_on_root = 1

# 是否在构建前清理

# 编译模式
android.release_artifact = apk

[buildozer]

# 允许root用户运行
allow_root = 1

# 日志等级
log_level = 2

# 显示构建警告
show_build_warnings = True

# 工作线程数
build_dir = ./build

# 日志文件
log_file = buildozer.log

# 是否使用颜色输出
colorize_build = True

# Pyarmor配置
pyarmor_distify = False

# Pyarmor路径
pyarmor_path = 

# 预构建APK
presplash_filename = presplash.png

# 图标
icon_filename = icon.png

# 主题颜色
orientation = portrait

# python-for-android版本
p4a.packages_path = /tmp/packages
