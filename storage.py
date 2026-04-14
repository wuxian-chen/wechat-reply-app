"""
消息存储模块
保存聊天历史和配置
"""
import os
import json
from datetime import datetime


class MessageStorage:
    """消息存储"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.messages = []
        self.load()
        
    def load(self):
        """加载历史消息"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            except:
                self.messages = []
                
    def save(self):
        """保存消息"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
            
    def add(self, sender, message, reply=""):
        """添加消息"""
        self.messages.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sender': sender,
            'message': message,
            'reply': reply,
            'used': False
        })
        self.save()
        
    def get_all(self):
        """获取所有消息"""
        return self.messages
        
    def get_recent(self, limit=10):
        """获取最近的消息"""
        return self.messages[-limit:]
        
    def get_by_sender(self, sender):
        """获取指定联系人的消息"""
        return [m for m in self.messages if m['sender'] == sender]
        
    def update_reply(self, index, reply):
        """更新回复"""
        if 0 <= index < len(self.messages):
            self.messages[index]['reply'] = reply
            self.messages[index]['used'] = True
            self.save()
            
    def mark_used(self, index):
        """标记为已使用"""
        if 0 <= index < len(self.messages):
            self.messages[index]['used'] = True
            self.save()
            
    def clear(self):
        """清空所有消息"""
        self.messages = []
        self.save()
        
    def get_stats(self):
        """获取统计信息"""
        total = len(self.messages)
        used = sum(1 for m in self.messages if m.get('used', False))
        return {
            'total': total,
            'used': used,
            'unused': total - used,
            'senders': list(set(m['sender'] for m in self.messages))
        }


class ConfigValidator:
    """配置验证"""
    
    @staticmethod
    def validate_api_key(api_key):
        """验证API Key格式"""
        if not api_key:
            return False, "API Key不能为空"
            
        if not api_key.startswith('sk-'):
            return False, "API Key格式错误，应以sk-开头"
            
        if len(api_key) < 30:
            return False, "API Key长度不足"
            
        return True, "验证通过"
        
    @staticmethod
    def validate_contact_name(name):
        """验证联系人名称"""
        if not name:
            return False, "联系人名称不能为空"
            
        if len(name) > 20:
            return False, "联系人名称过长"
            
        return True, "验证通过"
