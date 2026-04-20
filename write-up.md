# Design Rationale — Daily Reflection Tree

**Vikram Singh | DT Fellowship Assignment**

---

## Why These Questions

Every question was designed to surface a real psychological distinction — not to quiz, but to create a moment of honest self-recognition. The test I used: would a real person at 7pm actually pause on this, or would they click through?

**Axis 1 (Locus)** — The opening question ("pick one word for today") isn't about locus of control directly. It's a mood anchor. The word the employee chooses — Productive vs. Frustrating — primes a different emotional lens for the follow-up. Someone who said "Frustrating" needs a different first question than someone who said "Productive." The routing handles this. The follow-up questions then surface Rotter's distinction without naming it: did you look for what you could control, or did you wait? Did your preparation drive the outcome, or luck?

**Axis 2 (Orientation)** — Entitlement is invisible to the person carrying it. The design challenge was surfacing it without triggering defensiveness. The question "Was there a moment today where you felt the effort you put in wasn't being recognized?" is neutral — it doesn't imply the feeling is wrong. But the answer options (A: "I deserved more" vs. D: "recognition wasn't on my mind") reveal where the employee actually sits without shaming either position. Organ's OCB framework informed the contribution side: stepping in without being asked is the behavioral signature of contribution orientation.

**Axis 3 (Radius)** — Maslow's 1969 self-transcendence work (the level above self-actualization) frames this axis. The question "whose experience comes to mind first?" routes the employee to different branches based on how wide their default frame is — self, team, colleague, or customer. The progressive routing (self → team → other) mirrors the actual spectrum. Batson's perspective-taking research informed the follow-up: awareness without action is the typical failure mode, which is why the branch from A3_Q1_SELF explicitly asks "did you act on what you noticed?"

---

## Branching Design Decisions

**Mood-gating at the start.** The Axis 1 opening branches immediately on the opening word. A "Productive" day leads to "what drove it?" — a question about agency attribution. A "Frustrating" day leads to "what was your first move?" — a question about reactive vs. responsive behavior. Same underlying construct (locus of control), different surface texture. This keeps the tree feeling like a conversation, not a survey.

**Axis 2 parallel tracks.** Contribution and entitlement paths ask structurally similar questions from different angles. The contribution track asks "did giving feel like a drain?" — testing sustainability. The entitlement track asks "what did feeling overlooked make you want to do?" — testing whether recognition-seeking drives behavior. Both converge on a unified reflection pool (mixed, contribution, entitlement) at the end, which keeps the tree manageable.

**Axis 3 convergence.** All three Axis 3 entry points (self, team, other) eventually converge on either A3_Q2_EXPAND or A3_Q2_NARROW. This is intentional — someone who started self-centric but showed curiosity about others gets routed to EXPAND, not penalized for the opening answer. The signal tally matters more than any single answer.

**The summary uses state, not templates.** The summary node interpolates `{axis1.summary}`, `{axis2.summary}`, and `{axis3.summary}` — each resolved from the dominant signal tally, not from a fixed mapping to a single answer. This means the summary reflects the whole conversation, not just the last question.

---

## Trade-offs

- **3–4 options per question, not 5.** More options create decision fatigue. 3–4 well-designed options that genuinely span the spectrum beat 5 that overlap. I removed options when I couldn't distinguish between them honestly.
- **No free text.** The constraint in the brief is the right call. Free text requires classification (LLM or rules) and creates ambiguity. Fixed options force the designer to anticipate the real spectrum, which is the harder and more valuable work.
- **Bridge nodes auto-advance.** They don't ask for input. The transition between axes should feel like a natural gear change, not another prompt.
- **Reflections don't score.** A1_R_EXT doesn't say "you have an external locus." It says "somewhere in there, you made a call — what was it?" The goal is self-discovery, not diagnosis.

---

## What I'd Improve With More Time

1. **Streak awareness.** The tree has no memory across sessions. A second-session tree that references "yesterday you said Frustrating — today?" would create continuity without LLM inference.
2. **Deeper Axis 2 branching.** The current entitlement track is shallower than I'd like. A third question probing the gap between effort invested and outcome received would sharpen it.
3. **A "skip" option.** Some questions may not land on a given day. A graceful "none of these fit" exit that routes to the next axis without recording a signal would make the tool more honest.
4. **User testing with real employees.** I tested the options against imagined personas (and LLM-simulated personas). Real employees would surface option wording that sounds right in theory but fails in practice.

---

## Sources

- Rotter, J. B. (1966). *Generalized expectancies for internal versus external control of reinforcement.* Psychological Monographs.
- Dweck, C. S. (2006). *Mindset: The New Psychology of Success.*
- Campbell, W. K., et al. (2004). Psychological entitlement: Interpersonal consequences and validation of a self-report measure. *Journal of Personality Assessment.*
- Organ, D. W. (1988). *Organizational Citizenship Behavior: The Good Soldier Syndrome.*
- Maslow, A. H. (1969). Various meanings of transcendence. *Journal of Transpersonal Psychology.*
- Batson, C. D. (2011). *Altruism in Humans.*
