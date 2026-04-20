# Daily Reflection Tree — DT Fellowship Assignment

A deterministic end-of-day reflection agent. No LLM at runtime. Same answers → same path → same reflection. Every time.

---

## Structure

```
dt-fellowship/
├── tree/
│   └── reflection-tree.json     ← Part A: full tree data (50+ nodes)
├── agent/
│   └── agent.py                 ← Part B: Python CLI walker
├── transcripts/
│   ├── persona-1-victor-transcript.md
│   └── persona-2-victim-transcript.md
├── write-up.md                  ← Design rationale (2 pages)
└── README.md
```

---

## Running the Agent

**Requirements:** Python 3.7+. Optional: `colorama` for coloured output.

```bash
# Install optional dependency
pip install colorama

# Run from project root
python agent/agent.py

# Or specify tree path explicitly
python agent/agent.py --tree tree/reflection-tree.json
```

The agent loads `tree/reflection-tree.json` by default. It walks the tree, waits for numbered input at question nodes, auto-advances at all other node types, and prints a summary at the end.

No internet connection required. No API keys. No LLM calls.

---

## Reading the Tree

The tree is stored as JSON with a flat list of nodes. Each node has:

| Field | Purpose |
|---|---|
| `id` | Unique node identifier |
| `parentId` | Parent node (builds the hierarchy) |
| `type` | `start`, `question`, `decision`, `reflection`, `bridge`, `summary`, `end` |
| `text` | What the employee sees. Supports `{node_id.answer}` and `{axis1.summary}` interpolation |
| `options` | For questions: fixed choices. For decisions: routing rules (`answer=X\|Y:TARGET_ID`) |
| `target` | Explicit jump target (overrides child-finding) |
| `signal` | What this node records: `axis1:internal`, `axis2:contribution`, etc. |

**Decision node routing syntax:**
```
"answer=Productive|Mixed:A1_Q1_HIGH"
```
→ If the previous answer was "Productive" or "Mixed", go to node `A1_Q1_HIGH`.

Multiple rules are separated in the options array. First match wins.

**Signal accumulation:**
Signals are tallied per axis. At summary time, the dominant pole (highest tally) determines which summary template is used.

---

## Tree Coverage

| Requirement | Minimum | This Tree |
|---|---|---|
| Total nodes | 25+ | 50 |
| Question nodes | 8+ | 14 |
| Decision nodes | 4+ | 14 |
| Reflection nodes | 4+ | 8 |
| Bridge nodes | 2+ | 2 |
| Axes covered | 3 | 3 |
| Options per question | 3–5 | 4 each |
| Summary node | 1 | 1 + templates |

---

## How the Three Axes Flow

```
Axis 1: Locus (Victim ↔ Victor)
  Opening mood anchor → Agency attribution → Deliberate choice moment
  Reflections: internal / mixed / external

      ↓ BRIDGE

Axis 2: Orientation (Entitlement ↔ Contribution)
  Giving vs. receiving → Discretionary effort → Drain or meaning?
  Reflections: contribution / mixed / entitlement

      ↓ BRIDGE

Axis 3: Radius (Self ↔ Altrocentric)
  Whose experience first? → Awareness vs. action → Perspective shift
  Reflections: altrocentric / collective / self

      ↓ SUMMARY (interpolated from state tallies)
```

Each axis builds on the previous. The contribution questions are easier to answer honestly after the locus reflection. The radius questions land differently after the contribution reflection.

---

## Design Philosophy

- **No moralizing.** The "victim" path ends with "Hard day. The fact you're here doing this is the whole point." — not a lecture.
- **The tree meets people where they are.** A bad day is handled differently than a good one from the first question.
- **Fixed options force honest design.** The constraint of no free text means every option had to genuinely represent how a real person might answer. That's the harder and more valuable work.
- **State, not scripts.** The summary node doesn't have pre-written stories — it assembles from signal tallies. Same structure, different content, based on the actual path taken.
