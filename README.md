# 智声科技 AI 音频资源智能匹配平台

## 本地运行

PowerShell：

```powershell
$env:DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
python server.py
```

打开 `http://127.0.0.1:4173/ai-agent`。API Key 只从后端环境变量读取，不要写入 `app.js`、HTML 或 Git 仓库。

## 接口

前端请求 `POST /api/chat`，请求体为：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "我想找一个说唱混音师"}
  ]
}
```

后端代理到 DeepSeek Chat Completions，并以 `text/event-stream` 转发流式响应。浏览器端会把每一轮用户消息和 assistant 消息保存在当前对话中，下一次请求自动携带最近 30 条消息。

后端默认模型是 `deepseek-chat`，可通过服务端环境变量 `DEEPSEEK_MODEL` 替换，不需要修改或重新暴露前端代码。

## 生产部署

使用 `Dockerfile` 部署到支持容器的服务，并在服务的环境变量/密钥管理中配置 `DEEPSEEK_API_KEY`。前端和 `/api/chat` 最好使用同一域名；如果前后端分域，设置 `CHAT_API_URL` 和严格的 `ALLOWED_ORIGINS`。

当前 GitHub Pages 仅能托管静态前端，不能安全运行这个后端代理，因此不能直接把 DeepSeek Key 放进 GitHub Pages。
