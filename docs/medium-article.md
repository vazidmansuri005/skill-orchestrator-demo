# Stop Stuffing Your Prompt: An Architecture for Scaling LLM Agents

### Why "add one more capability" quietly kills your agent — and the progressive-disclosure design that keeps per-request cost flat as you scale.

Every agent starts the same way: one system prompt, a few instructions, a couple of tools. It works. So you add another capability. Then another. Six weeks later your prompt is 6,000 tokens of instructions for forty different jobs, latency is up, the bill is up, and — the part nobody warns you about — the agent is getting *worse*.

That is not a model problem. It is an architecture problem. This article is the architecture: **skills, a router, a knowledge base, and progressive disclosure.** There's a runnable demo at the end.

---

## The real bottleneck is context, not capability

Here is the naive way to make an agent do more: every new capability adds its instructions to the one big prompt. That gives you a per-request token cost that grows **O(n)** with the number of things the agent *can* do — even though any single request uses exactly one of them.

You pay for that twice:

1. **Money and latency.** Every request ships every instruction for every capability. At 40 capabilities you're sending ~24,000 tokens to answer a question that needs ~600.
2. **Quality.** This is the one that surprises people. As you pile in instructions, the relevant 3% gets buried in irrelevant text. Signal-to-noise drops, the model loses the thread ("lost in the middle"), and accuracy *falls* as you add capability. More context is not more capability — past a point it's less.

So the reframe that fixes everything: **you don't have a capability problem, you have a context-selection problem.** The goal is never to fit everything into the window. It's to load only what *this* request needs.

---

## Capabilities as software, not as one prompt

Three primitives. That's the whole architecture.

- **Skill** — a single-responsibility unit. One job, one file: instructions, optional code, and metadata. (`generate test cases`, `write a bug report`, `triage a flaky test`, `draft release notes`.)
- **Router (orchestrator)** — one entry point that reads the request and selects (and sequences) the skills it needs. You never invoke skills by hand.
- **Knowledge base (KB)** — shared facts that skills *reference* instead of inlining (conventions, formats, domain facts).

This is just **separation of concerns + lazy loading**, applied to prompts instead of code. Everything below is the consequence of taking that seriously.

---

## Anatomy of a skill

A skill is a markdown file with structured frontmatter:

```markdown
---
name: bug-report
description: Write a structured, triage-ready bug report from a crash or defect.
when_to_use: User reports a crash, defect, regression, or unexpected behavior.
keywords: [bug, crash, defect, regression, repro]
reads: [bug-report-format, project-facts]
---

# Bug Report
Convert a raw observation into a report an engineer can act on without follow-up.
1. Restate the problem: what happened vs. what was expected.
2. Pin the environment...
```

Two engineering points that matter more than they look:

- **The `description` is not documentation — it is the routing signal.** At selection time it is often the *only* thing the router sees about this skill. It must be a precise, discriminative one-liner. Write descriptions for the router, not for a human reading docs.
- **`reads:` declares KB dependencies explicitly.** That makes loading deterministic and auditable — you know exactly what context a skill will pull before it runs.

---

## Progressive disclosure: the mechanism that makes it scale

This is the core idea. Context loads in **three tiers**:

```
Tier 1  (always loaded):   every skill's name + description   -> the index
Tier 2  (on selection):    the chosen skill's full body
Tier 3  (on demand):       only the KB docs that skill's `reads:` declares
```

- **Tier 1** is the index. A handful of tokens per skill. It is *all the router needs* to choose. It is the only thing whose cost grows with the number of skills.
- **Tier 2** loads the chosen skill's instructions — only after it's been selected.
- **Tier 3** pulls only the KB documents that skill declared — not the whole knowledge base.

### The token math

With `N` skills of average body size `S`, and `M` KB docs of average size `K`:

```
Naive context        ≈  N·S  +  M·K  +  request     (grows with N and M)
Orchestrated context ≈  N·d  +  1·S  +  ~1.5·K + request
                          ^ d = a tiny one-line description
```

The only term in the orchestrated cost that grows with `N` is the cheap index (`N·d`). Everything else is constant per request. **Naive is O(n); orchestrated is ~O(1) per request.**

Concretely, from the demo:

| skills | naive | orchestrated | saved |
|-------:|------:|-------------:|------:|
| 4 | 2,411 | 817 | 66% |
| 10 | 6,028 | 879 | 85% |
| 40 | 24,110 | 1,185 | 95% |

Adding the 40th skill costs every request *one extra description line*. Nothing else. That is the difference between an agent you can grow and one you can't.

And it's safe for **quality**, not just cost: the model routes over a small, high-signal index, then reasons over only the relevant skill and KB. You've converted an O(n) attention problem into an O(1) one.

---

## The router: code vs. model, and the tradeoff

There are two ways to do selection, and the choice is a real engineering decision.

**Deterministic (code).** Keyword or embedding similarity over the index. Cheap, fast, debuggable, no extra LLM call. Brittle on phrasing. The demo uses this to stay offline:

```python
def score(request, skill):
    req = request.lower()
    s = 0.0
    for kw in skill.get("keywords", []):
        if kw.lower() in req:
            s += 2.0
    haystack = f"{skill['description']} {skill['when_to_use']}"
    s += len(words(req) & words(haystack)) * 0.1
    return s

def route(request, index):
    return max(index, key=lambda sk: score(request, sk))
```

**Model-based.** One cheap LLM classification call over the Tier-1 index returns the skill(s). Robust to phrasing, handles ambiguity, costs one small call. This is what most production systems use.

The non-negotiable rule either way: **route over the index, never over full skill bodies.** The entire economic argument collapses if you have to load everything to decide what to load. This is also exactly why the index must stay cheap — with a model router you pay to send it on every request.

Once a skill is selected, loading Tiers 2 and 3 is mechanical:

```python
skill   = route(request, index)
body    = load_skill_body(skill)            # Tier 2
kb_docs = load_kb(skill["reads"])           # Tier 3 — only what it declares
context = assemble(index, skill, body, kb_docs, request)
```

**Multi-skill composition.** A request may need a sequence — "investigate this failure, then file a bug" → triage skill, then bug-report skill. The router returns an ordered set; the orchestrator runs them and threads state between them. Keep that composition explicit; implicit chaining is where these systems get unpredictable.

---

## The knowledge base: DRY for prompts

Many skills need the same facts — naming conventions, a severity matrix, domain definitions. Inline those into each skill and you get duplication, drift, and bloat. Externalize them into a KB and skills *reference* them:

- One **single source of truth**; fix a convention once.
- Skills stay small and focused.
- Context stays lean because a skill pulls only the KB slice it declared.

For a large KB, the static `reads:` dependency becomes a dynamic **retrieval** step — which is just progressive disclosure one level down: skills disclose KB on demand, and retrieval decides which slice. (Yes — your RAG layer *is* the Tier-3 mechanism.)

---

## The mental model: it's an operating system

This isn't a cute analogy; it's the same problem producing the same solution:

| OS | Agent |
|---|---|
| Scheduler / kernel | **Router** — decides what runs |
| Installed programs | **Skills** — each does one job |
| Filesystem | **Knowledge base** — shared state |
| Demand paging | **Progressive disclosure** — load only on access |

An OS doesn't load every program into RAM at boot. It keeps a table of what's installed and pages in code on access. Your agent shouldn't load every instruction into context on every request either. Same constraint (limited fast memory, many programs), same answer (load on demand).

---

## Where this gets hard (the production realities)

The architecture is simple. Operating it well is where the engineering lives.

1. **Routing accuracy is your #1 failure mode.** A mis-route is a wrong skill, which is a wrong answer. Treat the router as a **classifier and eval it** — build a labeled set of `request → expected skill(s)` and track precision/recall. Don't ship a router you haven't measured.
2. **Descriptions *are* routing accuracy.** Most mis-routes trace back to vague or overlapping descriptions. Iterate them against your router eval, not your aesthetic sense.
3. **Skill granularity.** Too coarse and skills overlap so the router can't choose; too fine and you drown in orchestration overhead and brittle chains. Rule of thumb: one job per skill, and if two skills always fire together, merge them.
4. **Composition & state.** Multi-skill flows need a state contract — decide whether the orchestrator passes structured state between skills or they share a scratchpad. Make it explicit.
5. **Know when *not* to.** Below ~5 skills, the index and routing overhead aren't worth it — use one prompt. This pattern earns its complexity at scale.
6. **Security / trust boundary.** If skills or KB content can come from untrusted sources, a crafted description can hijack routing and KB text is untrusted input (prompt injection). Treat your skill/KB registry as a trust boundary.
7. **Observability.** Log which skill and which KB docs were loaded per request. That log is simultaneously your debugger and the data you eval the router on.

---

## How this maps to the tools you already use

This is not a niche trick — it's the convergent architecture of modern agent frameworks:

- **Claude Agent Skills** — `SKILL.md` with `name`/`description`, metadata always loaded, body and bundled files loaded on demand. This article's design *is* that model.
- **MCP (Model Context Protocol)** — tools and resources exposed with descriptions; the model selects over those descriptions. A router over an index.
- **LangGraph / multi-agent systems** — routing nodes and sub-agents are skills with an orchestrator around them.
- **RAG** — the KB tier. Retrieval is dynamic progressive disclosure.

Learn the four primitives — skill, router, KB, progressive disclosure — and you can reason about all of these instead of memorizing each framework's vocabulary.

---

## Takeaways

- Growing one prompt to add capability scales **O(n)** in tokens and *degrades* quality. It's the default, and it's a trap.
- **Skills + router + KB + progressive disclosure** makes per-request cost ~**O(1)**: cost, latency, and quality all improve together because they're all downstream of context size.
- **Route over a cheap index; load bodies and KB on demand.** Never load everything to decide what to load.
- **Descriptions are routing signal** — write and eval them as such.
- **Eval the router like a classifier.** It's the main thing that breaks.
- It's **demand paging for prompts.**

---

### Run it

A ~150-line, zero-dependency demo — one command prints the token comparison and the scaling curve:

```bash
git clone https://github.com/vazidmansuri005/skill-orchestrator-demo
cd skill-orchestrator-demo
python demo.py "write a bug report for the login crash on staging"
python demo.py --scale 40
```

→ **github.com/vazidmansuri005/skill-orchestrator-demo**
