"""排序. 用法: SUANLI_API_KEY=xxx python3 rerank.py"""
import json, os, urllib.request
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
body = {"model": "qwen/qwen3-reranker-8b",
        "query": "cat", "documents": ["a cat", "a dog"]}
req = urllib.request.Request(BASE + "/rerank", data=json.dumps(body).encode(),
    method="POST", headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    d = json.loads(r.read())
for it in d["results"]:
    print(f"OK index={it['index']} score={it['relevance_score']} text={it['document']['text']!r}")
