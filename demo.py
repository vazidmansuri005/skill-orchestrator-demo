"""Show the token cost of two ways to give an agent the same capabilities.

  naive         -> stuff EVERY skill + EVERY KB doc into one mega-prompt
  orchestrated  -> router loads only the matched skill + the KB it references

Usage:
    python demo.py "write a bug report for the login crash on staging"
    python demo.py --scale 40        # project the cost as the skill library grows
"""

import sys

import orchestrator as orch
from token_utils import count_tokens, tokenizer_name


def naive_context(request, index):
    """The 'just put everything in the prompt' approach."""
    parts = [orch.index_as_context(index)]
    all_kb = set()
    for skill in index:
        parts.append(f"\n# Skill: {skill['name']}\n{orch.load_skill_body(skill)}")
        all_kb.update(skill.get("reads", []))
    for name, text in orch.load_kb(sorted(all_kb)).items():
        parts.append(f"\n# Knowledge base: {name}\n{text}")
    parts.append(f"\n# User request\n{request}")
    return "\n".join(parts)


def run_request(request):
    index = orch.load_skill_index()

    naive = naive_context(request, index)
    naive_tokens = count_tokens(naive)

    skill = orch.route(request, index)
    body = orch.load_skill_body(skill)
    kb_docs = orch.load_kb(skill.get("reads", []))
    orchestrated = orch.assemble_context(request, index, skill, body, kb_docs)
    orch_tokens = count_tokens(orchestrated)

    saved = (1 - orch_tokens / naive_tokens) * 100 if naive_tokens else 0

    print(f'\nRequest: "{request}"')
    print(f"Tokenizer: {tokenizer_name()}\n")
    print(f"  Naive (every skill + every KB inline):  {naive_tokens:>7,} tokens")
    print(f"  Orchestrated (router + only what's used): {orch_tokens:>6,} tokens")
    print(f"  -> {saved:.0f}% fewer tokens for the same answer\n")
    print(f"  Routed to:    {skill['name']}  (1 of {len(index)} skills)")
    loaded = ", ".join(kb_docs) or "none"
    print(f"  KB loaded:    {loaded}  (of {_total_kb(index)} total docs)\n")
    return naive_tokens, orch_tokens


def _total_kb(index):
    all_kb = set()
    for s in index:
        all_kb.update(s.get("reads", []))
    return len(all_kb)


def project_scale(n):
    """Hold avg skill/KB size constant; show how each approach scales to N skills."""
    index = orch.load_skill_index()
    bodies = [count_tokens(orch.load_skill_body(s)) for s in index]
    avg_skill = sum(bodies) / len(bodies)
    kb_tokens = [count_tokens(t) for t in orch.load_kb(_all_kb_names(index)).values()]
    avg_kb = sum(kb_tokens) / len(kb_tokens) if kb_tokens else 0
    index_line = avg_skill * 0.04  # ~one short description line per skill

    print(f"\nProjection (avg skill ~{avg_skill:.0f} tok, avg KB doc ~{avg_kb:.0f} tok)\n")
    print(f"  {'skills':>7} | {'naive':>10} | {'orchestrated':>12} | saved")
    print(f"  {'-'*7} | {'-'*10} | {'-'*12} | -----")
    for count in sorted({len(index), 10, n, max(n, 40)}):
        naive = count * avg_skill + count * avg_kb
        orchestrated = count * index_line + avg_skill + 1.5 * avg_kb
        saved = (1 - orchestrated / naive) * 100
        print(f"  {count:>7} | {naive:>10,.0f} | {orchestrated:>12,.0f} | {saved:.0f}%")
    print("\n  Naive grows linearly. Orchestrated stays ~flat — that's the point.\n")


def _all_kb_names(index):
    names = set()
    for s in index:
        names.update(s.get("reads", []))
    return sorted(names)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--scale":
        project_scale(int(args[1]) if len(args) > 1 else 40)
    elif args:
        run_request(" ".join(args))
    else:
        run_request("write a bug report for the login crash on staging")
