"""
AI回复生成模块
调用通义千问API生成智能回复
"""
import json
import urllib.request
import urllib.error


class AIReplyGenerator:
    """AI回复生成器"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = "qwen-turbo"
        self.api_url = "https://dashscope.aliyuncs.com/completion-mode/v1"
        
    def generate_reply(self, message, style="温柔体贴"):
        """生成回复建议"""
        if not self.api_key:
            return ["❌ 请先配置API Key"]
            
        prompt = self._build_prompt(message, style)
        
        try:
            result = self._call_api(prompt)
            return self._parse_result(result)
        except Exception as e:
            return [f"❌ 生成失败: {str(e)}"]
            
    def _build_prompt(self, message, style):
        """构建提示词"""
        return f"""你是一个贴心的男友，请根据女友的消息给出3-5个回复建议。

女友消息：{message}

要求：
1. 风格：{style}
2. 每条建议20字以内
3. 适合情侣间的甜蜜对话
4. 用数字序号分隔开

回复建议："""
        
    def _call_api(self, prompt):
        """调用API"""
        data = {
            "model": self.model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "temperature": 0.8,
                "max_tokens": 200,
                "result_format": "message"
            }
        }
        
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            self.api_url,
            data=json_data,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
            
    def _parse_result(self, result):
        """解析API返回结果"""
        try:
            output = result.get('output', {})
            choices = output.get('choices', [])
            
            if choices:
                text = choices[0].get('message', {}).get('content', '')
                
                # 提取回复建议
                suggestions = []
                lines = text.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # 去掉序号
                    if line[0].isdigit() and '.' in line[:5]:
                        line = line.split('.', 1)[1].strip()
                        
                    if line and len(line) <= 50:
                        suggestions.append(line)
                        
                return suggestions[:5] if suggestions else ["💭 没有生成合适的回复"]
                
            return ["❌ API返回格式错误"]
            
        except Exception as e:
            return [f"❌ 解析失败: {str(e)}"]
            
    def generate_reply_with_context(self, message, chat_history, style="温柔体贴"):
        """基于上下文生成回复"""
        if not self.api_key:
            return ["❌ 请先配置API Key"]
            
        # 构建上下文
        history_text = ""
        for item in chat_history[-5:]:
            history_text += f"女友: {item['message']}\n你: {item['reply']}\n"
            
        prompt = f"""你是一个贴心的男友，正在和女友聊天。请根据对话上下文，给出回复建议。

【对话历史】
{history_text}

【女友最新消息】
{message}

要求：
1. 风格：{style}，自然、甜蜜
2. 每条建议25字以内
3. 考虑之前的对话内容
4. 用数字序号分隔

回复建议："""
        
        try:
            result = self._call_api(prompt)
            return self._parse_result(result)
        except Exception as e:
            return [f"❌ 生成失败: {str(e)}"]


# 测试代码
if __name__ == "__main__":
    generator = AIReplyGenerator("sk-7dcefd079c424374aec6336651f4c41d")
    
    test_messages = [
        "今天好累啊",
        "亲爱的在干嘛呀",
        "我想你了，呜呜",
        "我们周末去哪里玩呀？"
    ]
    
    print("=" * 50)
    print("AI回复生成测试")
    print("=" * 50)
    
    for msg in test_messages:
        print(f"\n📩 女友: {msg}")
        replies = generator.generate_reply(msg)
        for i, reply in enumerate(replies, 1):
            print(f"   {i}. {reply}")
