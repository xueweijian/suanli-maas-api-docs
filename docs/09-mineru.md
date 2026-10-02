# 09 · mineru 端点深挖：没有专有端点，真身是 chat 里的 VLM（半可用）

> 结论先行：`mineru/mineru2.5-pro-2604-1.2b` 在 MaaS 上**没有** `/file_parse` 这类专有端点
> （`POST /v1/parse`、`/file_parse`、`/ocr` 等 7 个猜测路径全部 404），
> 它的真身就是 `POST /v1/chat/completions` 里的 Qwen2-VL 架构模型——
> 但网关把特殊 token 剥掉了，版面坐标只能看不能用。**能聊，不能干活。**

## 官方 MinerU 是怎么调的（对照）

MinerU 官方（opendatalab/MinerU）有两套东西，别混：

1. **自部署 `mineru-api`**：`POST /file_parse` 传 PDF/图，回 markdown。这是 GPU 容器服务，
   共绩在弹性部署另有[预制 minerU 镜像](https://docs.suanli.cn/serverless/prefab/mineru)
   （4090 + `USE_API=true` + 8000 端口），和 MaaS 不是一套。
2. **VLM 模型本体**（[opendatalab/MinerU2.5-Pro-2604-1.2B](https://huggingface.co/opendatalab/MinerU2.5-Pro-2604-1.2B)）：
   Qwen2-VL 架构 1.2B 参数，走 OpenAI 兼容的 `/v1/chat/completions`，
   官方 `mineru-vl-utils` 的 `http-client` 后端调的正是这个端点
   （源码：`vlm_client/http_client.py`，`chat_url = server_url + /v1/chat/completions`，
   默认图在前文在后）。

MaaS 接的是第 2 种：纯 LLM 网关视角，一个 VLM 模型。

## 两步流程还原（官方 `two_step_extract`）

官方解析一张图要两步（`mineru_client.py`）：

1. **版面检测**：整图缩到 1036×1036，prompt `\nLayout Detection:`，
   采样 `temperature=0.0, top_p=0.01, top_k=1, repetition_penalty=1.0`，
   输出 `box_start…box_end + ref_start(type)ref_end + rotate标记` 的坐标行，
   本地 `parse_layout_output` 切块；
2. **分块识别**：每个块裁出来再调一次，prompt 按类型换
   （`\nText Recognition:` / `\nTable Recognition:` / `\nFormula Recognition:`），
   最后拼 markdown。

## MaaS 实测：三处对不上，只能看不能用

```bash
# 版面 prompt：坐标谱系正确，但特殊 token 被网关剥掉
curl -s $BASE/chat/completions -H "Authorization: Bearer $SUANLI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mineru/mineru2.5-pro-2604-1.2b",
       "messages":[{"role":"system","content":"You are a helpful assistant."},
                   {"role":"user","content":"\nLayout Detection:"}],
       "max_tokens":512,"temperature":0.0}'
```

| # | 现象 | 证据 |
|---|---|---|
| 1 | 版面 prompt 回**坐标谱系**（`100 000 999 019header…`），但**没有** `<\|box_start\|>` 等标记 | `assets/mineru_layout.json` 全文 511 字 |
| 2 | 采样参数全套照抄官方（`top_k/repetition_penalty/skip_special_tokens/vllm_xargs`）**照样无标记**，`skip_special_tokens:False` 也救不回来 | 网关层剥离 |
| 3 | 喂真文档图（1036×1036，含 MinerU/revenue/表格数字）：回包 0/6 命中，全是 `055 057…text` 坐标行；即使官方同构顺序（图前文后）也一样 | `probe/mineru_iso.py` |

第 3 条最致命：坐标行是对着真图算的（多行不同 bbox），说明视觉链路是通的；
但 block 类型**永远是 `text`/`header`**（从没出现过 table/equation/image），content 永远空——
第二步"按类型裁块识别"根本转不起来。顺带，`hi` 这类普通对话回空 content，
`completions(legacy)` 回 `HelloHelloHello…` 复读，`responses` 回空 output：
凡是不触发它版面/OCR 记忆的输入，它都只会空转或复读。

## 那 MaaS 上的 mineru 到底能干嘛

- ✅ 当"版面检测器"看热闹：喂图能拿回一堆坐标行，证明视觉编码器活着
- ❌ 当文档解析用：类型全标 `text`、无 content、特殊 token 被剥，拼不出 markdown
- ❌ 当 LLM 聊天用：空 content / 复读
- 真要解析 PDF：走弹性部署的预制 minerU 镜像（`/file_parse`），或 `mineru.net` 官方 API，
  别在 MaaS 这个模型上浪费 token

## 复现脚本

爆破 7 个猜测路径 + image_url 喂图：`probe/mineru_probe.py`；
合成文档图终极验证：`probe/mineru_final.py`；
vl-utils 同构（图前文后 + 全套采样）：`probe/mineru_iso.py`。
官方源码对照：`mineru-vl-utils/mineru_vl_utils/vlm_client/http_client.py`
（chat 端点）、`mineru_client.py`（`DEFAULT_PROMPTS` / `two_step_extract`）。
