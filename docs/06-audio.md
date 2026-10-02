# 06 · 语音转写 `POST /v1/audio/transcriptions`

`qwen/qwen3-asr-1.7b` 用 chat 调会拿到"假 200"：`content: "language None<asr_text>"`。
真转写走本端点，multipart 表单，已验证 200。

```bash
curl -s --max-time 120 $BASE/audio/transcriptions \
  -H "Authorization: Bearer $SUANLI_API_KEY" \
  -F model='qwen/qwen3-asr-1.7b' -F file=@voice.wav
```

真实回包（`assets/asr_transcribe.json` 原文；输入是合成的 2 秒 440Hz 正弦波，无语音，所以 `text` 为空，
但链路是通的，`usage.seconds=2` 对得上音频时长）：

```json
{"text":"","usage":{"type":"duration","seconds":2}}
```

要测真人声：换一段中文 wav（16kHz 单声道最稳），`text` 即转写结果。
`examples/audio_transcribe.py` 会现场合成 2 秒测试音再上传，零准备开跑。
