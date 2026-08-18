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

## AI 智能混音第一阶段

打开 `/ai-mixing`，可上传最多 4 个 WAV/MP3 文件并分别指定主人声、第二人声/和声、Adlib、伴奏。服务端会创建 Mix Job，调用 DeepSeek 生成音乐类型和默认方案 `ZHISHENG_DEFAULT_MIX`，然后等待 Windows Local Agent 领取任务。

第一阶段默认 `MIX_EXECUTION_MODE=manual`。Local Agent 会把音频下载到本地 Job 工作目录，并等待 Studio One 将最终 WAV 导出到该目录的 `output` 文件夹；只有检测到真实输出后，任务才会变为 `completed`。`manual_test_output=true` 仅用于测试任务链，页面会明确标注测试输出，不代表专业混音结果。

### Local Agent 启动

1. 复制 `local_agent/config.example.json` 为本机未提交的 `local_agent/config.json`。
2. 填写 `server_url`、`studio_one_template` 和本机工作目录。
3. 在 PowerShell 配置令牌并启动：

```powershell
$env:MIX_SERVER_URL = "https://你的 CloudBase 域名"
$env:MIX_AGENT_TOKEN = "与服务端相同的随机令牌"
python local_agent/agent.py
```

服务端需要配置 `MIX_EXECUTION_MODE=manual`、`MIX_AGENT_TOKEN`、`MIX_MAX_FILE_SIZE_MB=100` 和 `MIX_MAX_FILES=4`。Studio One 自动化接入后，只替换 `local_agent/studio_one_adapter.py` 的实现，不改变网页和任务 API。
