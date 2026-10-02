# 03 · 向量 `POST /v1/embeddings`

chat 里调 embedding 会吃 body-400（HTTP 200 + body `code:400`），必须走本端点。两个模型都验证通过。

```bash
curl -s $BASE/embeddings \
  -H "Authorization: Bearer $SUANLI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3-embedding-8b","input":"hello"}'
```

| 模型 | 向量维度 | 说明 |
|---|---|---|
| `qwen/qwen3-embedding-4b` | **2560** | 轻量，检索够用 |
| `qwen/qwen3-embedding-8b` | **4096** | 更大，精度/成本二选一 |

Python：

```python
from openai import OpenAI
client = OpenAI(api_key="你的 MaaS Key", base_url="https://api.suanli.cn/v1")
v = client.embeddings.create(model="qwen/qwen3-embedding-8b", input="hello")
print(len(v.data[0].embedding))  # 4096
```

真实回包（`assets/emb8b.json` 原文，向量截断留前 8 维，原文同理；`usage.prompt_tokens=2`）：

```json
{"id":"embd-890c26c7df6d67f0","object":"list","created":1790911410,
 "model":"Qwen3-Embedding-8B",
 "data":[{"index":0,"object":"embedding",
  "embedding":[0.0296630859375,0.0125732421875,-0.01523590087890625,-0.046173095703125,
   0.0033321380615234375,-0.01457977294921875,-0.0224761962890625,0.00392913818359375]}],
 "usage":{"prompt_tokens":2,"total_tokens":2,"completion_tokens":0,"prompt_tokens_details":null}}
```
