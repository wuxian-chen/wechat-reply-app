"""
微信智能回复APP - 主程序
功能：监听微信消息，自动生成回复建议
"""
import os
import json
import threading
import re
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

# 导入自定义模块
from ai_reply import AIReplyGenerator
from storage import MessageStorage

# 配置路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
HISTORY_PATH = os.path.join(os.path.dirname(__file__), 'chat_history.json')


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "qwen": {
            "api_key": "sk-7dcefd079c424374aec6336651f4c41d",
            "model": "qwen-turbo"
        },
        "monitor": {
            "contact_name": "女友",
            "check_interval": 3,
            "enabled": True
        },
        "reply": {
            "min_suggestions": 3,
            "max_suggestions": 5
        }
    }
    
    @classmethod
    def load(cls):
        """加载配置"""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        """保存配置"""
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)


class FloatingWindow:
    """悬浮窗 - 显示回复建议"""
    
    def __init__(self, app):
        self.app = app
        self.popup = None
        self.suggestions = []
        
    def show(self, message, sender, suggestions):
        """显示悬浮窗"""
        self.suggestions = suggestions
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        header = BoxLayout(size_hint_y=0.1)
        title = Label(
            text=f'💬 {sender}发来消息:',
            font_size='16sp',
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        header.add_widget(title)
        content.add_widget(header)
        
        # 消息内容
        msg_label = Label(
            text=message,
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=0.2,
            text_size=(Window.size[0] - 40, None),
            halign='left',
            valign='top'
        )
        content.add_widget(msg_label)
        
        # 分割线
        divider = BoxLayout(size_hint_y=0.02, size_hint_x=1)
        with divider.canvas:
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(size=divider.size, pos=divider.pos)
        content.add_widget(divider)
        
        # 回复建议列表
        scroll = ScrollView(size_hint_y=0.55, do_scroll_y=True)
        suggestions_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=8,
            padding=[0, 5]
        )
        suggestions_layout.bind(minimum_height=suggestions_layout.setter('height'))
        
        for i, suggestion in enumerate(suggestions[:5]):
            btn = Button(
                text=f'{i+1}. {suggestion}',
                font_size='13sp',
                size_hint_y=None,
                height='50sp',
                background_color=(0.2, 0.6, 0.9, 1),
                on_press=lambda x, s=suggestion: self.copy_and_close(s)
            )
            suggestions_layout.add_widget(btn)
        
        scroll.add_widget(suggestions_layout)
        content.add_widget(scroll)
        
        # 底部按钮
        bottom = BoxLayout(size_hint_y=0.1, spacing=10)
        close_btn = Button(
            text='关闭',
            background_color=(0.5, 0.5, 0.5, 1),
            on_press=lambda x: self.dismiss()
        )
        refresh_btn = Button(
            text='重新生成',
            background_color=(0.9, 0.5, 0.2, 1),
            on_press=lambda x: self.app.regenerate_replies(message, sender)
        )
        bottom.add_widget(close_btn)
        bottom.add_widget(refresh_btn)
        content.add_widget(bottom)
        
        # 创建弹出窗口
        self.popup = Popup(
            title='💡 智能回复建议',
            content=content,
            size_hint=(0.95, 0.7),
            auto_dismiss=False,
            title_color=(1, 1, 1, 1),
            title_size='18sp'
        )
        
        # 设置背景色
        with self.popup.content_parent.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.popup.content_parent.rect = Rectangle(
                size=self.popup.content_parent.size,
                pos=self.popup.content_parent.pos
            )
        
        self.popup.open()
        
    def copy_and_close(self, text):
        """复制并关闭"""
        Clipboard.copy(text)
        self.app.show_toast('已复制到剪贴板!')
        self.dismiss()
        
    def dismiss(self):
        """关闭悬浮窗"""
        if self.popup:
            self.popup.dismiss()
            self.popup = None


class MainScreen(Screen):
    """主界面"""
    
    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(**kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text='💕 微信智能回复助手',
            font_size='24sp',
            size_hint_y=0.15,
            color=(1, 0.5, 0.5, 1)
        )
        layout.add_widget(title)
        
        # 状态显示
        self.status_label = Label(
            text='🟢 服务已就绪',
            font_size='16sp',
            size_hint_y=0.1,
            color=(0.5, 1, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        # 配置区域
        config_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        
        # 联系人名称
        config_box.add_widget(Label(text='👤 女友微信名/备注:', font_size='14sp', size_hint_y=0.2))
        self.contact_input = TextInput(
            hint_text='请输入女友的微信名或备注',
            size_hint_y=0.25,
            multiline=False
        )
        config_box.add_widget(self.contact_input)
        
        # API Key
        config_box.add_widget(Label(text='🔑 通义千问API Key:', font_size='14sp', size_hint_y=0.2))
        self.api_key_input = TextInput(
            hint_text='sk-xxxxxxxx',
            size_hint_y=0.25,
            multiline=False,
            password=True
        )
        config_box.add_widget(self.api_key_input)
        
        layout.add_widget(config_box)
        
        # 监听开关
        switch_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        switch_box.add_widget(Label(text='🔔 开启消息监听:', font_size='14sp'))
        self.monitor_switch = Switch(active=False)
        self.monitor_switch.bind(active=self.on_switch_active)
        switch_box.add_widget(self.monitor_switch)
        layout.add_widget(switch_box)
        
        # 按钮区域
        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.15)
        
        save_btn = Button(
            text='💾 保存配置',
            background_color=(0.2, 0.7, 0.3, 1),
            on_press=lambda x: self.save_config()
        )
        test_btn = Button(
            text='🧪 测试API',
            background_color=(0.3, 0.5, 0.9, 1),
            on_press=lambda x: self.test_api()
        )
        history_btn = Button(
            text='📜 历史记录',
            background_color=(0.8, 0.6, 0.2, 1),
            on_press=lambda x: self.show_history()
        )
        
        btn_box.add_widget(save_btn)
        btn_box.add_widget(test_btn)
        btn_box.add_widget(history_btn)
        layout.add_widget(btn_box)
        
        self.add_widget(layout)
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        config = ConfigManager.load()
        self.contact_input.text = config.get('monitor', {}).get('contact_name', '')
        self.api_key_input.text = config.get('qwen', {}).get('api_key', '')
        self.monitor_switch.active = config.get('monitor', {}).get('enabled', False)
        
    def save_config(self):
        """保存配置"""
        config = ConfigManager.load()
        config['monitor']['contact_name'] = self.contact_input.text.strip()
        config['qwen']['api_key'] = self.api_key_input.text.strip()
        config['monitor']['enabled'] = self.monitor_switch.active
        
        ConfigManager.save(config)
        self.app.show_toast('✅ 配置已保存!')
        
    def test_api(self):
        """测试API连接"""
        api_key = self.api_key_input.text.strip()
        if not api_key:
            self.app.show_toast('❌ 请先输入API Key')
            return
            
        self.app.ai_generator = AIReplyGenerator(api_key)
        test_result = self.app.ai_generator.generate_reply("你好呀，今天过得怎么样？")
        
        if test_result and not test_result[0].startswith('❌'):
            self.app.show_toast('✅ API连接成功!')
            self.status_label.text = '🟢 API已连接'
        else:
            self.app.show_toast(f'❌ {test_result[0] if test_result else "API连接失败"}')
            self.status_label.text = '🔴 API连接失败'
            
    def on_switch_active(self, instance, value):
        """开关状态改变"""
        config = ConfigManager.load()
        config['monitor']['enabled'] = value
        ConfigManager.save(config)
        
        if value:
            self.app.start_monitoring()
            self.status_label.text = '🟢 正在监听消息...'
        else:
            self.app.stop_monitoring()
            self.status_label.text = '🟡 监听已停止'
            
    def show_history(self):
        """显示历史记录"""
        self.app.manager.current = 'history'


class HistoryScreen(Screen):
    """历史记录页面"""
    
    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(**kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题栏
        header = BoxLayout(size_hint_y=0.1)
        header.add_widget(Label(text='📜 聊天历史记录', font_size='20sp', size_hint_x=0.7))
        back_btn = Button(
            text='返回',
            size_hint_x=0.3,
            on_press=lambda x: setattr(self.app.manager, 'current', 'main')
        )
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # 清空按钮
        clear_box = BoxLayout(size_hint_y=0.08)
        clear_btn = Button(
            text='🗑️ 清空历史',
            background_color=(0.9, 0.3, 0.3, 1),
            on_press=lambda x: self.clear_history()
        )
        clear_box.add_widget(clear_btn)
        layout.add_widget(clear_box)
        
        # 历史记录列表
        self.scroll = ScrollView(size_hint_y=0.82)
        self.history_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=5
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.scroll.add_widget(self.history_layout)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)
        self.load_history()
        
    def load_history(self):
        """加载历史记录"""
        self.history_layout.clear_widgets()
        history = self.app.storage.get_all()
        
        if not history:
            self.history_layout.add_widget(Label(
                text='暂无历史记录',
                font_size='16sp',
                size_hint_y=None,
                height='100sp'
            ))
            return
            
        # 显示最近的20条
        for item in history[-20:]:
            card = self.create_history_card(item)
            self.history_layout.add_widget(card)
            
    def create_history_card(self, item):
        """创建历史记录卡片"""
        card = BoxLayout(orientation='vertical', size_hint_y=None, height='120sp')
        card.padding = 10
        
        with card.canvas.before:
            Color(0.2, 0.2, 0.25, 1)
            card.rect = Rectangle(size=card.size, pos=card.pos)
        card.bind(pos=self.update_rect, size=self.update_rect)
        
        time_label = Label(
            text=item.get('time', ''),
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.2,
            halign='left'
        )
        
        sender_label = Label(
            text=f"👤 {item.get('sender', '未知')}:",
            font_size='13sp',
            color=(0.5, 0.8, 1, 1),
            size_hint_y=0.2,
            halign='left'
        )
        
        content_label = Label(
            text=item.get('message', ''),
            font_size='12sp',
            color=(1, 1, 1, 1),
            size_hint_y=0.35,
            text_size=(card.width - 20, None),
            halign='left',
            valign='top'
        )
        
        reply_label = Label(
            text=f"💬 {item.get('reply', '')}",
            font_size='12sp',
            color=(0.7, 1, 0.7, 1),
            size_hint_y=0.25,
            text_size=(card.width - 20, None),
            halign='left'
        )
        
        card.add_widget(time_label)
        card.add_widget(sender_label)
        card.add_widget(content_label)
        card.add_widget(reply_label)
        
        return card
        
    def update_rect(self, instance, value):
        """更新背景"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        
    def clear_history(self):
        """清空历史"""
        self.app.storage.clear()
        self.load_history()
        self.app.show_toast('✅ 历史已清空')


class WeChatReplyApp(App):
    """微信智能回复应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = ConfigManager.load()
        self.ai_generator = AIReplyGenerator(self.config['qwen']['api_key'])
        self.storage = MessageStorage(HISTORY_PATH)
        self.floating_window = FloatingWindow(self)
        self.monitor_thread = None
        self.running = False
        
    def build(self):
        """构建应用"""
        Window.clearcolor = (0.1, 0.1, 0.15, 1)
        
        # 创建屏幕管理器
        self.manager = ScreenManager()
        
        # 添加主界面
        main_screen = MainScreen(self, name='main')
        self.manager.add_widget(main_screen)
        
        # 添加历史页面
        history_screen = HistoryScreen(self, name='history')
        self.manager.add_widget(history_screen)
        
        return self.manager
        
    def on_start(self):
        """应用启动"""
        if self.config['monitor']['enabled']:
            self.start_monitoring()
            
    def on_pause(self):
        """应用暂停"""
        return True
        
    def on_resume(self):
        """应用恢复"""
        pass
        
    def show_toast(self, message):
        """显示提示"""
        # 使用Popup模拟Toast
        popup = Popup(
            content=Label(text=message, font_size='16sp'),
            size_hint=(0.6, 0.2),
            auto_dismiss=True,
            background_color=(0.2, 0.2, 0.2, 1)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        
    def start_monitoring(self):
        """启动消息监听"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止消息监听"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def monitor_loop(self):
        """监听循环 - 模拟消息接收"""
        # 注意：实际使用需要通过Android AccessibilityService
        # 这里只是演示接口调用
        
        # 获取联系人名称
        contact_name = self.config['monitor'].get('contact_name', '女友')
        
        # 模拟消息（实际从无障碍服务获取）
        # self.receive_message("女友", "今天好累啊...")
        
    def receive_message(self, sender, message):
        """接收消息并生成回复"""
        # 保存消息
        self.storage.add(sender, message, '')
        
        # 生成回复
        suggestions = self.ai_generator.generate_reply(message)
        
        if suggestions:
            # 显示悬浮窗
            Clock.schedule_once(
                lambda dt: self.floating_window.show(message, sender, suggestions),
                0
            )
            
    def regenerate_replies(self, message, sender):
        """重新生成回复"""
        suggestions = self.ai_generator.generate_reply(message)
        
        if suggestions:
            self.floating_window.dismiss()
            Clock.schedule_once(
                lambda dt: self.floating_window.show(message, sender, suggestions),
                0.1
            )


# 启动应用
if __name__ == '__main__':
    WeChatReplyApp().run()
