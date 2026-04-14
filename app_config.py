"""
配置文件
微信智能回复APP配置
"""

APP_CONFIG = {
    # 应用信息
    'app_name': '微信智能回复',
    'app_version': '1.0.0',
    'app_author': 'SmartReply Team',
    
    # 联系人设置
    'monitor': {
        'contact_name': '女友',  # 目标联系人名称
        'check_interval': 3,      # 检查间隔（秒）
        'enabled': True,         # 默认启用
    },
    
    # AI回复设置
    'reply': {
        'min_suggestions': 3,    # 最少回复建议数
        'max_suggestions': 5,     # 最多回复建议数
        'reply_style': '温柔体贴',  # 回复风格
        'max_history': 100,      # 最大历史记录数
    },
    
    # API设置
    'api': {
        'provider': 'qwen',      # API提供商
        'model': 'qwen-turbo',   # 模型
        'temperature': 0.8,      # 创造性参数
        'max_tokens': 200,        # 最大token数
    },
    
    # UI设置
    'ui': {
        'theme': 'dark',          # 主题
        'font_size': 14,          # 字体大小
        'primary_color': '#FF6B6B',  # 主色调
    },
    
    # 通知设置
    'notification': {
        'show_preview': True,    # 显示消息预览
        'sound': True,           # 声音提示
        'vibrate': False,        # 震动提示
    },
    
    # 高级设置
    'advanced': {
        'debug_mode': False,     # 调试模式
        'log_level': 'INFO',     # 日志级别
        'auto_start': True,      # 开机自启
        'battery_optimization': False,  # 电池优化
    }
}


def get_config(key, default=None):
    """获取配置值"""
    keys = key.split('.')
    value = APP_CONFIG
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
            
    return value


def update_config(key, new_value):
    """更新配置值"""
    keys = key.split('.')
    config = APP_CONFIG
    
    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]
        
    config[keys[-1]] = new_value
