#!/usr/bin/env python3
"""OpenAI-compatible host adapter for `scripts/assets.py run-evals`.

Per invocation: reads one JSON case on stdin (``id``, ``prompt``,
``asset_digest``), builds a runtime-grounded context pack, calls a chat
completion endpoint, and prints ``{"answer": str, "retrieved_refs": [str]}``
on stdout. The harness runs this with cwd = ``dist/runtime``.

Configuration (environment variables):

- ``XP_EVAL_API_BASE``  OpenAI-compatible base URL, e.g. ``https://open.bigmodel.cn/api/paas/v4``
- ``XP_EVAL_API_KEY``   bearer token
- ``XP_EVAL_MODEL``     model name, e.g. ``glm-4.7``

v1 limits (deliberate): single completion call, no tool loop; knowledge cards
are selected by character n-gram overlap, which is keyword recall, not semantic
retrieval. Replace this packer with an agentic host when one is available.

``--self-test`` exercises the protocol shape offline (no network, canned answer)
so the harness contract can be verified without credentials.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

import yaml

MAX_CARDS = 10
REQUEST_TIMEOUT = int(os.environ.get('XP_EVAL_TIMEOUT', '90'))
CONTEXT_CHAR_LIMIT = 24000


def load_cards() -> list[dict]:
    cards = []
    for name in ('principle_cards.yaml', 'case_cards.yaml', 'claim_audit.yaml',
                 'contradictions.yaml', 'model_registry.yaml'):
        path = os.path.join('02_knowledge', name)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                for record in yaml.safe_load(fh) or []:
                    cards.append(record)
    return cards


def card_text(record: dict) -> str:
    parts = []
    for value in record.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(v) for v in value)
    return ' '.join(parts)[:600]


def grams(text: str, sizes=(2, 3)) -> set[str]:
    flat = re.sub(r'\s+', '', text)
    out = set()
    for size in sizes:
        out.update(flat[i:i + size] for i in range(len(flat) - size + 1))
    return out


def select_cards(prompt: str, cards: list[dict], limit: int = MAX_CARDS) -> list[dict]:
    prompt_grams = grams(prompt)
    scored = sorted(((len(prompt_grams & grams(card_text(c))), c) for c in cards),
                    key=lambda pair: -pair[0])
    return [c for score, c in scored if score > 0][:limit]


def context_pack(prompt: str) -> tuple[str, list[str]]:
    """Return (system prompt, refs actually packed)."""
    with open(os.path.join('03_agent', 'METHOD_POLICY.md'), encoding='utf-8') as fh:
        policy = fh.read()
    cards = select_cards(prompt, load_cards())
    blocks, refs = [], []
    for card in cards:
        cid = card.get('id') or card.get('model_id')
        refs.append(cid)
        refs.extend(card.get('source_refs') or [])
        blocks.append(f"[{cid}] {card_text(card)}")
    body = '\n'.join(blocks) or '(no matching knowledge cards)'
    system = (f"{policy}\n\n## 本次可用的知识卡（按关键词粗筛，非语义检索）\n{body}"
              "\n\n回答用户问题：区分【材料明确表达】【材料归纳】【工程化外推】【材料不足】；"
              "引用给出来源 ID；材料不足时明确说明，不虚构。")
    return system[:CONTEXT_CHAR_LIMIT], refs


def call_model(system: str, prompt: str) -> str:
    base = os.environ.get('XP_EVAL_API_BASE', '').rstrip('/')
    key = os.environ.get('XP_EVAL_API_KEY', '')
    model = os.environ.get('XP_EVAL_MODEL', '')
    if not (base and key and model):
        raise SystemExit('set XP_EVAL_API_BASE, XP_EVAL_API_KEY and XP_EVAL_MODEL')
    payload = json.dumps({'model': model, 'temperature': 0.2, 'max_tokens': 2048,
                          'messages': [{'role': 'system', 'content': system},
                                       {'role': 'user', 'content': prompt}]}).encode('utf-8')
    request = urllib.request.Request(
        base + '/chat/completions', data=payload, method='POST',
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        body = json.loads(response.read().decode('utf-8'))
    return body['choices'][0]['message']['content']


def main() -> int:
    if '--self-test' in sys.argv[1:]:
        payload = {'id': 'self-test', 'prompt': '自模型是什么', 'asset_digest': 'x' * 64}
    else:
        payload = json.loads(sys.stdin.read().decode('utf-8'))
    system, refs = context_pack(payload['prompt'])
    if '--self-test' in sys.argv[1:]:
        answer = 'SELF-TEST: context pack built with %d refs' % len(set(refs))
    else:
        answer = call_model(system, payload['prompt'])
    print(json.dumps({'answer': answer, 'retrieved_refs': sorted(set(refs))},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
