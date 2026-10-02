# 08 · 坑位记录（5 个，全部亲踩）

## 1. 业务拒绝藏 body 里（最坑）

embedding / rerank 用 chat 调时，HTTP 外层 **200**，body 却是：

```json
{"error":{"message":"The model does not support Chat Completions API",
 "type":"BadRequestError","param":"","code":400}}
```

判通必须同时满足：`http==200 且 body 有 choices/data/results 且无 error 字段`。
`examples/` 里所有脚本都按这个规则判定。

## 2. 生图 chat 直接 404

```json
{"error":{"message":"Not Found","type":"bad_response_status_code",
 "param":"","code":"bad_response_status_code"}}
```

别重试了，换 `POST /v1/images/generations`。

## 3. 生图很慢，超时别设 30s

flux 实测 60s+ 才回包（base64 约 1.68MB）。curl 加 `--max-time 180`，
Python `urlopen(..., timeout=180)`，否则会被客户端误杀。

## 4. 间歇 DNS 抖动 / 超时

沙箱到 `api.suanli.cn` 偶发 `Errno -3 Try again` / read timeout，
同一请求重试 2-3 次即过。脚本里统一 3 次重试 + 3s 间隔；
vl-32b 那次就是第 1 次超时、第 2 次 200。

## 5. App 模型列表缓存

App 里 "可用模型 (11)" 是旧缓存，线上实际 14 个。
refresh 模型列表后多出 omni / rerank / vl-30b / qwen3.8 / SD3.5。
以后以 `GET /v1/models` 为准，别以 App 截图为准。
