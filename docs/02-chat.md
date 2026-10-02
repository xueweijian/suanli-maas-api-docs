# 02 · 对话 `POST /v1/chat/completions`（OpenAI 兼容）

7 个模型真通，1 个占位符（ASR），1 个半可用（mineru，见 [09 深挖](09-mineru.md)）。

## 真通的 7 个 LLM

cURL 模板（把 `MODEL` 换成下表任一）：

```bash
curl -s $BASE/chat/completions \
  -H "Authorization: Bearer $SUANLI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"MODEL","messages":[{"role":"user","content":"hi"}],"max_tokens":32}'
```

| model 参数 | 实测回包 `model` 字段 | 备注 |
|---|---|---|
| `deepseek/deepseek-v4-flash-0731-free` | `DeepSeek-V4-Flash-0731` | 最稳的对照组：`hi` → `Hello! How can I help you today?` |
| `minimax/minimax-m2.5-awq` | `MiniMax-M2.5` | 首 token 走 reasoning，`content:null` 属正常，多要几个 token 即有正文 |
| `qwen/qwen3-32b` | `Qwen3-32B` | thinking 模型 |
| `qwen/qwen3.8-27b` | `Qwen3.8-27B` | `reasoning` 字段带思考过程 |
| `qwen/qwen3-omni-30b-a3b-instruct` | `Qwen3-Omni-30B-A3B-Instruct` | 纯文本直接聊；多模态能力未测 |
| `qwen/qwen3-vl-30b-a3b-instruct` | `Qwen3-VL-30B-A3B-Instruct` | 纯文本直接聊 |
| `qwen/qwen3-vl-32b-instruct` | `Qwen3-VL-32B-Instruct` | 偶发 DNS 超时，重试即过 |

Python（OpenAI SDK，官方文档同款姿势）：

```python
from openai import OpenAI
client = OpenAI(api_key="替换为你的 MaaS Key", base_url="https://api.suanli.cn/v1")
r = client.chat.completions.create(
    model="deepseek/deepseek-v4-flash-0731-free",
    messages=[{"role": "user", "content": "请用一句话解释什么是大语言模型。"}],
    max_tokens=1000, temperature=0.7,
)
print(r.choices[0].message.content)
```

真实回包（`assets/chat.json` 原文，`hi` + `max_tokens=32`）：

```json
{"id":"chatcmpl-87b447e839b90c72","object":"chat.completion","created":1790911411,
 "model":"DeepSeek-V4-Flash-0731",
 "choices":[{"index":0,"message":{"role":"assistant","content":"Hello! How can I help you today?",
 "refusal":null,"annotations":null,"audio":null,"function_call":null,"tool_calls":[],
 "reasoning":null},"logprobs":null,"finish_reason":"stop","stop_reason":null,"token_ids":null}],
 "usage":{"prompt_tokens":5,"total_tokens":15,"completion_tokens":10,"prompt_tokens_details":null}}
```

## ❌ 别用 chat 调这 4 个（对照证据）

```bash
# embedding：HTTP 200，但 body 是 400
{"error":{"message":"The model does not support Chat Completions API",
 "type":"BadRequestError","param":"","code":400}}
# 生图 flux / SD3.5：直接 404
{"error":{"message":"Not Found","type":"bad_response_status_code",
 "param":"","code":"bad_response_status_code"}}
```

## ⚠️ 1 个占位符 + 1 个半可用

| 模型 | chat 返回 | 结论 |
|---|---|---|
| `qwen/qwen3-asr-1.7b` | `content: "language None<asr_text>"` | 占位符。真转写走 [`audio/transcriptions`](06-audio.md)（已验证 200） |
| `mineru/mineru2.5-pro-2604-1.2b` | `hi`→空；`Layout Detection`→坐标行（特殊 token 被剥）；真图 0/6 命中 | 半可用：无专有端点（7 路径全 404），版面可看不可用。全文见 [`09-mineru.md`](09-mineru.md) |
