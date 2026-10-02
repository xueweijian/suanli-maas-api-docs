# suanli-maas-api-docs

共绩算力 MaaS（`api.suanli.cn/v1`）**非官方实测文档**：14 个模型的真实可用端点 + 可直接跑的请求示例。

官方文档（[使用大模型 Token](https://docs.suanli.cn/choose/llm)）只讲了 `POST /v1/chat/completions` 调 LLM，
但 `/v1/models` 里混着 embedding / rerank / 生图 / ASR / OCR——用 chat 调它们要么 404、要么 body 里藏 400、要么返回空。
本仓库把每个模型的**正确端点**全部实测一遍并给出证据。

- 文档网站：推库后开 GitHub Pages 即看（`index.html`，无构建，手机可读）
- 证据：[`assets/`](assets/) 下是真实响应的原文快照（向量只留前 8 维），样张 [`assets/flux_sample.png`](assets/flux_sample.png)
- 快照日期：2026-10-02，`GET /v1/models` 返回 `object=list, success=True`，共 **14** 个模型

## 30 秒速览

```bash
export SUANLI_API_KEY='你的 MaaS Key'   # 从 https://maas.suanli.cn/api-keys 获取
export BASE='https://api.suanli.cn/v1'

# 模型清单（14 个，比 App 缓存里的 11 个新）
curl -s $BASE/models -H "Authorization: Bearer $SUANLI_API_KEY" | python3 -c \
  "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"

# LLM 对话（7 个真 LLM 都走这里）
curl -s $BASE/chat/completions -H "Authorization: Bearer $SUANLI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek/deepseek-v4-flash-0731-free","messages":[{"role":"user","content":"hi"}],"max_tokens":32}'
```

## 模型 × 端点总表（全部实测）

| 模型 | 类型 | chat/completions | 正确端点 | 备注 |
|---|---|---|---|---|
| `deepseek/deepseek-v4-flash-0731-free` | LLM | ✅ 通 | chat | 对照组，`hi` → `Hello! How can I help you today?` |
| `minimax/minimax-m2.5-awq` | LLM | ✅ 通 | chat | 首 token 是 reasoning，content 为空属正常 |
| `qwen/qwen3-32b` | LLM | ✅ 通 | chat | thinking 模型 |
| `qwen/qwen3.8-27b` | LLM | ✅ 通 | chat | reasoning 字段带思考过程 |
| `qwen/qwen3-omni-30b-a3b-instruct` | 多模态 LLM | ✅ 通 | chat | 纯文本可直接聊 |
| `qwen/qwen3-vl-30b-a3b-instruct` | 视觉 LLM | ✅ 通 | chat | 纯文本可直接聊 |
| `qwen/qwen3-vl-32b-instruct` | 视觉 LLM | ✅ 通 | chat | 偶发 DNS 超时，重试即过 |
| `qwen/qwen3-embedding-4b` | embedding | ❌ body-400 | `POST /v1/embeddings` ✅ | 向量维度 **2560** |
| `qwen/qwen3-embedding-8b` | embedding | ❌ body-400 | `POST /v1/embeddings` ✅ | 向量维度 **4096** |
| `qwen/qwen3-reranker-8b` | rerank | ❌ body-400 | `POST /v1/rerank` ✅ | 注意不是 `/v1/v1/rerank` |
| `black-forest-labs/flux.1-krea-dev` | 文生图 | ❌ 404 | `POST /v1/images/generations` ✅ | 返回 `file://base64` PNG，慢（60s+），超时设 180s |
| `stabilityai/stable-diffusion-3.5-medium` | 文生图 | ❌ 404 | `POST /v1/images/generations` ✅ | 同上 |
| `qwen/qwen3-asr-1.7b` | ASR | ⚠️ 200 占位符 | `POST /v1/audio/transcriptions` ✅ | chat 回 `language None<asr_text>` 无用；转写端点 200，2s 音频回 `{"text":"","usage":{"seconds":2}}` |
| `mineru/mineru2.5-pro-2604-1.2b` | OCR/文档解析 | ⚠️ 200 空 content | 专有端点未知 | chat 调通但无内容，勿用 chat |

> ❌ body-400 指：HTTP 外层是 200，body 里是 `{"error":{"message":"The model does not support Chat Completions API","code":400}}`。
> 判通不能只看状态码，详见 [`docs/08-gotchas.md`](docs/08-gotchas.md)。

## 文档目录

- [`docs/01-overview.md`](docs/01-overview.md) —— Base URL / 鉴权 / Key 获取
- [`docs/02-chat.md`](docs/02-chat.md) —— 对话接口（7 LLM + 2 占位符）
- [`docs/03-embeddings.md`](docs/03-embeddings.md) —— 向量接口（维度 2560 / 4096）
- [`docs/04-rerank.md`](docs/04-rerank.md) —— 排序接口
- [`docs/05-images.md`](docs/05-images.md) —— 生图接口（base64 解码 + 样张）
- [`docs/06-audio.md`](docs/06-audio.md) —— ASR 转写接口
- [`docs/07-models.md`](docs/07-models.md) —— 14 模型全矩阵 + `/v1/models` 原始字段
- [`docs/08-gotchas.md`](docs/08-gotchas.md) —— 5 个坑（body-400 / 404 / 慢生图 / DNS 抖动 / App 缓存）

## 可运行示例

```bash
pip install -r examples/requirements.txt   # 零依赖其实也行，见各文件头
python3 examples/models_list.py
python3 examples/chat.py
python3 examples/embeddings.py
python3 examples/rerank.py
python3 examples/images.py            # 约 60-120s，产出 cat.png
python3 examples/audio_transcribe.py  # 自带合成 2s 测试音，无需准备音频
```

curl 版见各端点文档页，复制即跑。

## 责任声明

本仓库与共绩算力官方无关，是第三方实测记录。模型上下线频繁，`GET /v1/models` 永远以线上为准；
某个端点某天变了欢迎提 Issue / PR（最好附上脱敏后的响应体）。
