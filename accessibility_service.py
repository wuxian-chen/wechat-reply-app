"""
Android无障碍服务模块
监听微信消息通知
"""
import json
import os
import threading
from datetime import datetime


class AccessibilityServiceListener:
    """
    无障碍服务监听器
    
    注意：此模块需要配合Android端的AccessibilityService使用
    需要在AndroidManifest.xml中声明权限和服务
    """
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.monitoring = False
        self.callback = None
        self.contact_name = self.config.get('monitor', {}).get('contact_name', '女友')
        
    def _load_config(self, config_path):
        """加载配置"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def set_callback(self, callback):
        """设置消息回调"""
        self.callback = callback
        
    def set_contact(self, name):
        """设置监听联系人"""
        self.contact_name = name
        
    def start_monitoring(self):
        """开始监听"""
        self.monitoring = True
        # 在Android端启动AccessibilityService
        # self._start_android_service()
        
    def stop_monitoring(self):
        """停止监听"""
        self.monitoring = False
        # self._stop_android_service()
        
    def on_notification_received(self, notification):
        """
        处理接收到的通知
        由Android端无障碍服务调用
        """
        if not self.monitoring:
            return
            
        # 解析通知内容
        app_name = notification.get('app_name', '')
        sender = notification.get('sender', '')
        content = notification.get('content', '')
        
        # 只处理微信消息
        if app_name != '微信':
            return
            
        # 检查是否为目标联系人
        if not self._is_target_contact(sender):
            return
            
        # 调用回调
        if self.callback:
            self.callback(sender, content)
            
    def _is_target_contact(self, sender):
        """检查是否为目标联系人"""
        if not self.contact_name:
            return True
            
        return self.contact_name in sender
        
    def get_monitoring_status(self):
        """获取监听状态"""
        return {
            'monitoring': self.monitoring,
            'contact': self.contact_name,
            'timestamp': datetime.now().isoformat()
        }


class NotificationFilter:
    """通知过滤器"""
    
    # 微信包名
    WECHAT_PACKAGE = "com.tencent.mm"
    
    # 忽略的通知关键词
    IGNORE_KEYWORDS = [
        '转账', '微信支付', '微信红包', '微信收款',
        '微信运动', '腾讯新闻', '小程序'
    ]
    
    @classmethod
    def should_process(cls, notification):
        """判断是否需要处理"""
        # 检查包名
        if notification.get('package_name') != cls.WECHAT_PACKAGE:
            return False, "非微信应用"
            
        # 检查关键词
        content = notification.get('content', '')
        for keyword in cls.IGNORE_KEYWORDS:
            if keyword in content:
                return False, f"忽略: {keyword}"
                
        return True, "需要处理"
        
    @classmethod
    def parse_wechat_notification(cls, extras):
        """解析微信通知内容"""
        try:
            # 微信通知格式可能包含:
            # android.text - 通知文本
            # android.title - 通知标题(通常是发送者)
            # android.bigText - 通知详细内容
            
            sender = extras.get('android.title', '')
            content = extras.get('android.text', '')
            big_text = extras.get('android.bigText', '')
            
            # 合并内容
            if big_text:
                content = big_text
                
            return {
                'sender': sender,
                'content': content.strip()
            }
        except Exception as e:
            return None


# Java端需要实现的接口
class AndroidBridge:
    """
    Android桥接模块
    
    需要在Android端实现以下功能:
    1. 启动AccessibilityService
    2. 监听微信通知
    3. 提取通知内容
    4. 回调到Python端
    """
    
    def __init__(self):
        self.accessibility_listener = None
        
    def initialize(self, listener):
        """初始化"""
        self.accessibility_listener = listener
        
    def on_accessibility_event(self, event):
        """
        接收无障碍服务事件
        由Android端调用
        """
        if not self.accessibility_listener:
            return
            
        # 解析事件
        package_name = event.get('package_name', '')
        
        if package_name == 'com.tencent.mm':
            # 处理微信事件
            self._handle_wechat_event(event)
            
    def _handle_wechat_event(self, event):
        """处理微信事件"""
        event_type = event.get('event_type', '')
        
        # TYPE_NOTIFICATION_STATE_CHANGED - 通知状态变化
        if event_type == 'TYPE_NOTIFICATION_STATE_CHANGED':
            self._handle_notification(event)
            
        # TYPE_WINDOW_CONTENT_CHANGED - 窗口内容变化
        elif event_type == 'TYPE_WINDOW_CONTENT_CHANGED':
            self._handle_window_change(event)
            
    def _handle_notification(self, event):
        """处理通知事件"""
        # 提取通知文本
        text = event.get('text', [])
        if text:
            content = ' '.join(text)
            # 这里需要更复杂的逻辑来提取发送者和内容
            
    def _handle_window_change(self, event):
        """处理窗口变化"""
        # 可以监听微信聊天界面的变化
        pass
