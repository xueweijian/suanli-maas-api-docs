# 04 · 排序 `POST /v1/rerank`

`qwen/qwen3-reranker-8b` 在 chat 里同样吃 body-400，正确端点是本接口（注意前缀只有一层 `/v1`）。

```bash
curl -s $BASE/rerank \
  -H "Authorization: Bearer $SUANLI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"qwen/qwen3-reranker-8b","query":"cat","documents":["a cat","a dog"]}'
```

真实回包（`assets/rerank.json` 原文）：

```json
{"results":[
  {"document":{"multi_modal":null,"text":"a cat"},"index":0,"relevance_score":0.21142578125},
  {"document":{"multi_modal":null,"text":"a dog"},"index":1,"relevance_score":0.10174560546875}],
 "usage":{"prompt_tokens":6,"completion_tokens":0,"total_tokens":6,
  "prompt_tokens_details":{"cached_tokens":0,"text_tokens":0,"audio_tokens":0,"image_tokens":0}}}
```

`query` 越相关 `relevance_score` 越高（`a cat` 0.21 > `a dog` 0.10，符合预期）。

⚠️ 别写成 `POST /v1/v1/rerank`：base 已含 `/v1`，再拼一次会
`404 {"error":{"message":"Invalid URL (POST /v1/v1/rerank)"}}`。
