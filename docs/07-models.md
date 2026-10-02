# 07 · 模型全矩阵（`GET /v1/models`，2026-10-02 快照）

回包顶层：`{"object":"list","success":true,"data":[...]}`，共 **14** 个。
App 里显示的 11 个是旧缓存，refresh 后以这里为准。原文见 `assets/models_raw.json`。

| # | 模型 id | 支持的端点类型 | 实测结论 |
|---|---|---|---|
| 1 | `black-forest-labs/flux.1-krea-dev` | image-generation, openai | 生图走 images ✅，chat 404 |
| 2 | `deepseek/deepseek-v4-flash-0731-free` | openai | chat ✅ |
| 3 | `mineru/mineru2.5-pro-2604-1.2b` | openai | chat 假 200（空 content）⚠️ |
| 4 | `minimax/minimax-m2.5-awq` | openai | chat ✅ |
| 5 | `qwen/qwen3-32b` | openai | chat ✅ |
| 6 | `qwen/qwen3-asr-1.7b` | openai | chat 假 200（占位符）⚠️；转写走 audio ✅ |
| 7 | `qwen/qwen3-embedding-4b` | openai | embeddings ✅（2560 维），chat body-400 |
| 8 | `qwen/qwen3-embedding-8b` | openai | embeddings ✅（4096 维），chat body-400 |
| 9 | `qwen/qwen3-omni-30b-a3b-instruct` | openai | chat ✅ |
| 10 | `qwen/qwen3-reranker-8b` | openai | rerank ✅，chat body-400 |
| 11 | `qwen/qwen3-vl-30b-a3b-instruct` | openai | chat ✅ |
| 12 | `qwen/qwen3-vl-32b-instruct` | openai | chat ✅（偶发超时，重试） |
| 13 | `qwen/qwen3.8-27b` | openai | chat ✅ |
| 14 | `stabilityai/stable-diffusion-3.5-medium` | openai | 生图走 images ✅，chat 404 |

注意 `supported_endpoint_types` 仅供参考：两个生图模型标了 `image-generation`，
但实际路径仍是 OpenAI 兼容的 `/v1/images/generations`，不是另起一套。
