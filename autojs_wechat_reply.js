"auto";
// 微信智能回复助手 - Auto.js版本
// 使用方法：安装Auto.js APP后导入此脚本运行

// ============ 配置区域 ============
var CONFIG = {
    // 通义千问API配置
    apiKey: "sk-7dcefd079c424374aec6336651f4c41d",
    apiUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    model: "qwen-turbo",
    
    // 监控配置
    targetContact: "老大",  // 女友的微信备注名
    checkInterval: 2000,     // 检查间隔(毫秒)
    
    // 回复建议数量
    suggestionCount: 3
};

// ============ 主程序 ============

// 请求必要权限
requestScreenCapture();
if (!requestScreenCapture()) {
    toast("需要截图权限");
    exit();
}

// 悬浮窗显示回复建议
function showReplyWindow(suggestions) {
    var window = floaty.window(
        <vertical bg="#CC000000" padding="15">
            <text text="💕 智能回复建议" textColor="#FF6B9D" textSize="16sp" textStyle="bold"/>
            <text id="msg_preview" text="" textColor="#FFFFFF" textSize="12sp" margin="5 0"/>
            <scroll>
                <vertical id="suggestions" />
            </scroll>
            <button id="close" text="关闭" w="*" bg="#FF6B9D"/>
        </vertical>
    );
    
    window.close.click(() => {
        window.close();
    });
    
    // 添加建议按钮
    suggestions.forEach(function(s, i) {
        var btn = ui.inflate(
            <button text="" w="*" bg="#333333" textColor="#FFFFFF" style="Widget.AppCompat.Button.Borderless"/>
        , window.suggestions, true);
        btn.setText((i+1) + ". " + s);
        btn.click(function() {
            setClip(s);
            toast("已复制: " + s);
        });
    });
    
    window.setSize(400, -2);
    window.setPosition(device.width/2 - 200, 100);
}

// 调用通义千问API获取回复建议
function getReplySuggestions(message) {
    try {
        var response = http.postJson(CONFIG.apiUrl, {
            model: CONFIG.model,
            messages: [
                {
                    role: "system",
                    content: "你是一个恋爱助手。当女朋友发消息时，帮助男朋友生成合适的回复建议。回复要自然、有趣、有感情。每次给出3个不同风格的回复建议。"
                },
                {
                    role: "user", 
                    content: "女朋友说: \"" + message + "\"\n\n请给我3个回复建议，每个建议用数字编号，简短一点。"
                }
            ]
        }, {
            headers: {
                "Authorization": "Bearer " + CONFIG.apiKey,
                "Content-Type": "application/json"
            }
        });
        
        var result = response.body.json();
        if (result.choices && result.choices[0]) {
            return result.choices[0].message.content;
        }
        return "获取回复失败";
    } catch (e) {
        return "API调用错误: " + e;
    }
}

// 解析回复建议
function parseSuggestions(response) {
    var lines = response.split("\n");
    var suggestions = [];
    lines.forEach(function(line) {
        // 匹配 "1." "2." "3." 开头的行
        var match = line.match(/^\d+\.\s*(.+)$/);
        if (match) {
            suggestions.push(match[1].trim());
        }
    });
    return suggestions.length > 0 ? suggestions : [response];
}

// 监控微信消息
function monitorWechat() {
    toast("开始监控微信消息...\n目标联系人: " + CONFIG.targetContact);
    
    var lastNotification = "";
    
    events.on("notification", function(n) {
        if (n.getPackageName() == "com.tencent.mm") {
            var title = n.tickerText || "";
            var content = n.getText ? n.getText() : "";
            
            // 检查是否是目标联系人发来的消息
            if (title.indexOf(CONFIG.targetContact) >= 0) {
                var message = content || title.replace(CONFIG.targetContact, "").replace(":", "").trim();
                
                if (message && message != lastNotification) {
                    lastNotification = message;
                    toast("收到消息: " + message);
                    
                    // 获取回复建议
                    var response = getReplySuggestions(message);
                    var suggestions = parseSuggestions(response);
                    
                    // 显示悬浮窗
                    ui.post(function() {
                        showReplyWindow(suggestions);
                    });
                }
            }
        }
    });
    
    // 保持脚本运行
    setInterval(function(){}, 10000);
}

// 手动测试模式
function testMode() {
    dialogs.rawInput("输入女朋友发的消息:", "", function(message) {
        if (message) {
            toast("正在生成回复建议...");
            var response = getReplySuggestions(message);
            var suggestions = parseSuggestions(response);
            
            var choice = dialogs.singleChoice("选择回复", suggestions);
            if (choice >= 0) {
                setClip(suggestions[choice]);
                toast("已复制: " + suggestions[choice]);
            }
        }
    });
}

// ============ 启动菜单 ============
var mode = dialogs.singleChoice("选择模式", [
    "自动监控微信消息",
    "手动输入测试"
]);

if (mode == 0) {
    monitorWechat();
} else {
    testMode();
}
