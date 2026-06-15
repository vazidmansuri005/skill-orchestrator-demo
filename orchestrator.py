"""A tiny skill router that demonstrates *progressive disclosure*.

Three tiers of context loading — this is the whole idea:

    Tier 1  (always loaded):   skill name + description           -> the "index"
    Tier 2  (loaded on match): the selected skill's full body
    Tier 3  (loaded on demand): only the KB docs that skill references

So you can register 4 skills or 400 — a single request still only pays for the
handful actually in play. The router below uses simple keyword scoring to keep
the demo dependency-free and offline; in production you'd swap `route()` for a
single LLM classification call over the (cheap) Tier-1 index.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
KB_DIR = ROOT / "kb"


# --------------------------------------------------------------------------- #
# Frontmatter parsing (minimal YAML subset — no external deps)
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str):
    """Return (metadata_dict, body_str) for a `---`-delimited markdown file."""
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            items = [x.strip().strip("'\"") for x in raw[1:-1].split(",")]
            meta[key] = [x for x in items if x]
        else:
            meta[key] = raw
    return meta, body.strip()


# --------------------------------------------------------------------------- #
# Tier 1 — the index (cheap, always in context)
# --------------------------------------------------------------------------- #
def load_skill_index():
    """Load only name/description/routing metadata for every skill."""
    index = []
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        meta, _ = parse_frontmatter(skill_md.read_text())
        meta["path"] = skill_md
        meta.setdefault("keywords", [])
        meta.setdefault("reads", [])
        index.append(meta)
    return index


def index_as_context(index) -> str:
    """The compact text the model always sees: one line per skill."""
    lines = ["# Available skills", ""]
    for s in index:
        lines.append(f"- {s['name']}: {s.get('description', '')}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Routing — pick the skill(s) a request needs
# --------------------------------------------------------------------------- #
def _words(text: str):
    return set(re.findall(r"[a-z]+", text.lower()))


def score(request: str, skill) -> float:
    req = request.lower()
    s = 0.0
    for kw in skill.get("keywords", []):
        if kw.lower() in req:
            s += 2.0
    haystack = f"{skill.get('description', '')} {skill.get('when_to_use', '')}"
    s += len(_words(req) & _words(haystack)) * 0.1
    return s


def route(request: str, index):
    """Return the best-matching skill (highest score)."""
    ranked = sorted(index, key=lambda sk: score(request, sk), reverse=True)
    return ranked[0]


# --------------------------------------------------------------------------- #
# Tiers 2 & 3 — load only what the chosen skill needs
# --------------------------------------------------------------------------- #
def load_skill_body(skill) -> str:
    _, body = parse_frontmatter(skill["path"].read_text())
    return body


def load_kb(reads) -> dict:
    docs = {}
    for name in reads:
        doc = KB_DIR / f"{name}.md"
        if doc.exists():
            docs[name] = doc.read_text()
    return docs


def assemble_context(request, index, skill, body, kb_docs) -> str:
    """The exact text a real agent would send to the model for this request."""
    parts = [index_as_context(index), f"\n# Active skill: {skill['name']}\n", body]
    for name, text in kb_docs.items():
        parts.append(f"\n# Knowledge base: {name}\n{text}")
    parts.append(f"\n# User request\n{request}")
    return "\n".join(parts)
