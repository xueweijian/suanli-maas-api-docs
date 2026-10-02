# 01 · 总览：Base URL / 鉴权 / Key

> 快照日期 2026-10-02。官方文档只讲 chat，本仓库补全其余 4 类端点。

## 服务地址

| 项 | 值 |
|---|---|
| API Base URL | `https://api.suanli.cn/v1` |
| 模型广场 / Playground | `https://console.suanli.cn/models` |
| API Key 管理 | `https://maas.suanli.cn/api-keys` |
| 官方文档（只有 chat） | `https://docs.suanli.cn/choose/llm` |

注意 new-api 二次分发文档里让填 `https://api.suanli.cn`（不带 `/v1`），那是 new-api 渠道配置的写法；
**直接调 API 时 Base URL 必须带 `/v1`**，否则 `POST /v1/v1/rerank` 这种双前缀 404（见[坑位记录](08-gotchas.md)）。

## 鉴权

全端点统一 `Authorization: Bearer <MaaS Key>`：

```bash
export SUANLI_API_KEY='粘你的 MaaS Key'
export BASE='https://api.suanli.cn/v1'
curl -s $BASE/models -H "Authorization: Bearer $SUANLI_API_KEY" | head -c 300
```

Key 从 `https://maas.suanli.cn/api-keys` 新建（可设永不过期 + 无限额度）。

⚠️ **老 OpenAPI 的 `GONGJI_API_TOKEN` 不能复用**：调 `/v1/models` 会回
`502 billing-reader 返回 401 {"error":"Invalid SK"}`，必须新建 MaaS Key。

## 5 类端点一览

| 端点 | 用途 | 模型 |
|---|---|---|
| `POST /v1/chat/completions` | 对话（OpenAI 兼容） | 7 个真 LLM（见[对话页](02-chat.md)） |
| `POST /v1/embeddings` | 文向量 | embedding-4b（2560 维）/ 8b（4096 维） |
| `POST /v1/rerank` | 粗排/精排 | reranker-8b |
| `POST /v1/images/generations` | 文生图 | flux.1-krea-dev / SD3.5-medium，返回 `file://base64` PNG |
| `POST /v1/audio/transcriptions` | 语音转写 | qwen3-asr-1.7b（multipart 表单，见[音频页](06-audio.md)） |

## 连通性自检

```bash
curl -s -o /dev/null -w '%{http_code}\n' $BASE/models -H "Authorization: Bearer $SUANLI_API_KEY"
# 200 即通；无 Key 时 400 {"code":400,"message":"缺少用户凭证"}
```
