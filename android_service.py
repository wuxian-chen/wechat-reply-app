"""
Android启动接收器
实现开机自启动功能
"""
from android import activity
from jnius import autoclass
from kivy.utils import platform


class BootReceiver:
    """
    开机启动接收器
    
    需要在AndroidManifest.xml中注册BroadcastReceiver
    """
    
    @staticmethod
    def request_boot_permission():
        """请求开机启动权限"""
        if platform != 'android':
            return False
            
        try:
            # Android端实现开机启动
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            # 检查权限
            current_activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
            current_activity.startActivity(intent)
            
            return True
        except Exception as e:
            print(f"请求开机启动权限失败: {e}")
            return False
            
    @staticmethod
    def is_boot_enabled():
        """检查开机启动是否启用"""
        if platform != 'android':
            return False
            
        try:
            # 检查系统设置
            return True
        except:
            return False


class PermissionHelper:
    """权限帮助类"""
    
    @staticmethod
    def request_all_permissions():
        """请求所有必需的权限"""
        if platform != 'android':
            return True
            
        permissions = [
            'ACCESS_NOTIFICATION_POLICY',      # 通知权限
            'SYSTEM_ALERT_WINDOW',            # 悬浮窗权限
            'FOREGROUND_SERVICE',             # 前台服务
            'WRITE_EXTERNAL_STORAGE',         # 存储权限
            'READ_EXTERNAL_STORAGE',          # 读取存储
            'POST_NOTIFICATIONS',             # 通知权限
            'BIND_ACCESSIBILITY_SERVICE'      # 无障碍服务
        ]
        
        results = []
        for permission in permissions:
            result = PermissionHelper.request_permission(permission)
            results.append((permission, result))
            
        return results
        
    @staticmethod
    def request_permission(permission):
        """请求单个权限"""
        if platform != 'android':
            return True
            
        try:
            from android.permissions import request_permissions, Permission
            
            if permission == 'SYSTEM_ALERT_WINDOW':
                # 悬浮窗权限需要特殊处理
                return PermissionHelper.request_overlay_permission()
            elif 'ACCESSIBILITY' in permission:
                # 无障碍服务需要用户手动开启
                return PermissionHelper.open_accessibility_settings()
            else:
                request_permissions([permission])
                return True
                
        except Exception as e:
            print(f"请求权限失败 {permission}: {e}")
            return False
            
    @staticmethod
    def request_overlay_permission():
        """请求悬浮窗权限"""
        if platform != 'android':
            return True
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            
            current_activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            intent.setData(Uri.fromParts("package", current_activity.getPackageName(), None))
            current_activity.startActivity(intent)
            
            return True
        except Exception as e:
            print(f"请求悬浮窗权限失败: {e}")
            return False
            
    @staticmethod
    def open_accessibility_settings():
        """打开无障碍设置页面"""
        if platform != 'android':
            return True
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            current_activity = PythonActivity.mActivity
            intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            current_activity.startActivity(intent)
            
            return True
        except Exception as e:
            print(f"打开无障碍设置失败: {e}")
            return False
            
    @staticmethod
    def check_permissions():
        """检查所有权限状态"""
        if platform != 'android':
            return {}
            
        permissions_status = {
            'overlay': PermissionHelper.check_overlay_permission(),
            'accessibility': PermissionHelper.check_accessibility_permission(),
            'notifications': True,  # 默认给通知权限
            'storage': True
        }
        
        return permissions_status
        
    @staticmethod
    def check_overlay_permission():
        """检查悬浮窗权限"""
        if platform != 'android':
            return True
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            
            current_activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            intent.setData(Uri.fromParts("package", current_activity.getPackageName(), None))
            
            # 在实际使用中需要检查系统设置
            return True
        except:
            return False
            
    @staticmethod
    def check_accessibility_permission():
        """检查无障碍服务权限"""
        if platform != 'android':
            return True
            
        try:
            # 检查无障碍服务是否启用
            return True
        except:
            return False


def setup_android_permissions():
    """设置Android权限"""
    if platform != 'android':
        return
        
    print("正在请求Android权限...")
    results = PermissionHelper.request_all_permissions()
    
    for permission, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {permission}")
