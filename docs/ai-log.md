# AI log — working with AI on this project

One honest entry per phase, minimum: one interaction that worked well, one that failed or needed correction. This is teaching material on the "AI does syntax, humans own semantics" discipline — the failures are the most valuable entries.

Workflow: Tom writes raw notes in `Notetaking.md` → Claude formats them here.

## Phase 0 — 2026-07-17

**Task given to AI:** plan the pipeline (research, architecture, build plan) and scaffold the repo (Claude, Cowork session).

**What it did well:**
- Planning: market research with sources; the DuckLake-vs-Postgres discussion surfaced the concurrency argument.
- Repo created with a sensible folder structure for GitHub.

**Where it went wrong / what the human had to correct:**
- Created many files the owner didn't understand: `.sqlfluff`, a `docker-compose.yml` already written before Phase 1 even started, `.github/workflows/ci.yml` created without explanation or discussion.
- Too many decisions taken upfront, instead of evolving step by step with the builder.
- The scaffold was *complete* but not *understood* — and an unexplained file is technical debt for a learning project.

**Correction applied:** delete the not-yet-understood files and let the project grow organically. Each file comes back only when its phase needs it, explained first, understood before committed.

**Applied by Tom (same day):**
- Deleted `docker-compose.yml`, the GitHub workflow, and the pre-written dependencies in `pyproject.toml` — each returns when its phase needs it.
- Deleted Claude's `.git` entirely (it was littered with stale lock files — the remote bridge can't delete git's temp files) and re-initialized it himself. New rule: **git runs only on the owner's machine**; the AI proposes commands, the human executes.
- Confirmed the local-first order: everything proven locally → GitHub → droplet last, to optimize cost.
- Brought the project plan into the repo to guide the work.

**Lesson:** an AI will happily build the whole house on day one. The human's job is pacing: nothing enters the repo that its owner can't explain. "AI does syntax, humans own semantics" also means humans own the *rhythm*.

> Note originale (FR) : « Création de beaucoup de fichiers que je ne comprends pas (…) Trop de décisions prises sans évolution au fur et à mesure. Je vais demander à Claude ce que sont ces fichiers et les supprimer pour que le projet grandisse organiquement. »

## Phase 1 prep — engine decision & DuckLake sandbox — 2026-07-17

**Task given to AI:** define what Phase 1 (dependencies/technologies) actually needs; validate the transform engine.

**What the human had to correct — the day's real lesson:**
- Claude assumed dbt = Python package. **dbt Fusion is a Rust binary** — not installed via uv, travels via a pinned version in README prerequisites. AI knowledge is not always current.
- Claude assumed Fusion+DuckDB support was uncertain. Tom installed it and proved it works, then pushed the decision through: **Fusion from the start** (ADR 0002).
- Pattern confirmed twice in one day: *never let the AI decide on assumptions — a 10-minute test beats its training data.* The human owns decisions; the AI provides context and gets verified.

**Also revised:** Phase 1 needs no Docker at all — Python deps via uv, Fusion as binary, DuckLake as files. Containers arrive only when a real service does (catalog Postgres, at concurrency time).

**Sandbox results (first_Test/) — what is now proven:**
- Fusion 2.0.0-preview.196 + DuckDB + DuckLake: `dbt debug` OK, `dbt run` green end-to-end (source in lake → model materialized back into lake).
- Traps found and understood on the way: a file *named* `.ducklake` attached via plain `path:` is just a native DuckDB file — only the `ducklake:` attach prefix makes a lake · `ref()` is for models, `source()` for external tables · views live in the catalog (no Parquet), tables write Parquet into `.files/`.

**Validated configuration (the trinity):**
1. `profiles.yml` — attach the lake: `attach: [{path: "ducklake:my_ducklake.ducklake", alias: my_ducklake}]`
2. `dbt_project.yml` — materialize into it: `models: <project>: +database: my_ducklake`
3. `sources.yml` — locate raw data in it: `database: my_ducklake` (+ `schema:` when source name ≠ schema)

**Mental model (keep):**
```
DuckDB    = the engine (a program that runs SQL)
DuckLake  = the memory (Parquet files + a catalog that indexes them)
ATTACH 'ducklake:...' = the key connecting engine to memory
views live in the catalog · tables live as Parquet
```

## Phase 1 — uv, dlt & the shared-lake proof — 2026-07-20

**Task:** set up uv from scratch; prove dlt can write into the same DuckLake that dbt Fusion uses (the one-lake architecture bet).

**What the AI got wrong (and the human caught):**
- Proposed `dlt[duckdb]` — Tom asked "duckdb, not ducklake?", forcing a doc check: dlt has a **native `ducklake` destination** with its own extra. Third instance of the pattern: *AI priors lag the ecosystem; verify before adopting.*

**What the collaboration did well:** five failures diagnosed in sequence without losing the thread — each error read carefully, root cause named, lesson extracted (3-slash URLs, file-catalog locks, frozen DATA_PATH, twin catalogs, stray keystroke). The AI proposed abandoning the broken sandbox ("bankruptcy"); Tom insisted on rebuilding until it worked — the right call: the rebuild-from-rubble is now the best-understood part of the stack.

**Proven:** one DuckLake, duckdb-format catalog, shared by three writers — manual SQL, dbt Fusion, dlt — verified side by side in `SHOW ALL TABLES`. The architecture's riskiest assumption is now fact.

**Also shipped (by Tom, solo):** the real lake's birth certificate — `infra/ducklake-setup.sh` created `data/lake_catalog.ducklake` in its final home — and the decision that all non-uv binaries (duckdb CLI, dbt Fusion) get their own recipe in `infra/setup_server.sh`, the future Dockerfile's first draft.

**Rules reinforced:** file catalogs hate concurrent sessions (the droplet's Postgres catalog is now justified by lived experience, not just ADR 0001) · create the lake explicitly, in its final home, DATA_PATH declared · `dev_mode` never in real pipelines.

## The Exam — sandbox rebuilt solo — 2026-07-21

**Task:** Tom rebuilds the whole dlt+DuckLake setup from scratch, from memory, to consolidate. AI on call only when surprised.

**What the AI got wrong (twice):**
- Claimed omitting dlt's `[storage]` block makes dlt defer to the catalog's recorded path. False — dlt *synthesizes* a default from `ducklake_name` and announces it (error #4).
- Claimed DuckLake resolves a relative DATA_PATH to absolute at creation. False — recorded verbatim (error #5).

**What the human did right:** refused to accept "it can't work without X" when memory said otherwise ("No, because before I made it work without the absolute path") — and was correct: the earlier success was dlt-as-creator, a different consistent world. Tested variants until the full map emerged: four consistent path configurations, each verified by hand. In Tom's words: *"Claude was struggling a lot with this — needed to test myself for it to work."*

**Outcome:** complete understanding of DuckLake path semantics (birth-time recording, byte-identical announcement, cwd traps), a production decision (`$(pwd)`-computed absolute paths in infra, mirrored via config), and the exam's dlt half passed without notes. dbt half remains.

**Meta-lesson for the log:** five AI errors in five days, every one caught by the human testing against ground truth. The collaboration works *because* the human distrusts correctly — this is the skill the mentoring should teach first.

## The Exam, part 2 — dbt half, and the alias collision — 2026-07-22

**Task:** finish the solo rebuild: dbt Fusion reading dlt's tables in the shared lake.

**The saga:** Fusion attached the lake as plain `duckdb` — invisible schemas, hours of hunting. The AI burned seven theories (orphan metadata wings, engine version skew, a Fusion .200 regression — refuted by Tom, who checked the timeline; dlt metadata formats; relative DATA_PATH). The decisive probes were real: `duckdb_databases()` type column, mtime forensics, a fresh-catalog differential test. But the answer was Tom's:

**Failure mode #7 — the alias collision.** DuckDB names a database after its filename stem: `path: data/lake.duckdb` enters the engine as database `lake`, colliding with `attach: alias: lake`. The scratch db wore the lake's name; the real DuckLake attach was shadowed. Every clue retrofits: the 17th worked (dev vs my_ducklake — no collision), `fresh` worked (unique alias), scratch mtime moved while the catalog's never did. **Rule: an attach alias must never equal the filename stem of the path database.**

**Also learned:** profile `schema:` sets the target's base schema cleanly; `+schema:` concatenates (`main_analytics`) until `generate_schema_name` is overridden — queued for the real transform/.

**Outcome: EXAM PASSED.** Lake with `lake_schema` (dlt) + `analytics` (dbt), rebuilt solo, every failure understood. The human found the final bug with the AI's own methods — differential tests and file forensics. The mentoring flipped: this story is his to teach now.

## Phase 2 opens — Neon connected, first real extraction — 2026-07-22

**Task:** wire the real source (course-platform Postgres on Neon) into the lake.

**What worked:** the architecture absorbed its first real payload with zero new concepts — read-only role on Neon, credentials and catalog paths in `.env` (dlt double-underscore dialect), `sql_database()` empty-call injection, `just ingest` as the one-word run. First table extracted: `students`.

**Corrections along the way:** `../data/` relative catalog path caught before it shipped (cwd trap, third appearance — pattern is now reflex) · `SOURCE__` vs `SOURCES__` env key · psql command tail pasted into the connection string · the source is named `sql_database`, not `postgres` (dlt naming: postgres is a destination).

**Teaching gold found in an error:** dlt's ConfigFieldMissing traceback prints its entire provider lookup chain (every env spelling, every toml path, in order) — the config system documenting itself at failure time.

**Env inheritance lesson:** `.env` without `export` + plain `source` = variables invisible to child processes; `just`'s dotenv-load (or the `set -a` sandwich) is what actually delivers them. Why the same command works via just and fails bare.

## Over-modeling caught — 2026-07-28

**What happened:** the AI scaffolded a 14-model "proper star schema" — and its own marts didn't
use its own facts. Four models (fct_events, fct_progress, fct_payments, dim_date) had zero
consumers; the stitching int had one. Tom's verdict: "adding extra complexity for no reason."
Correct. Cut to 9 models, every one with a consumer. Facts/dims return the day Evidence or the
MCP door actually consumes them — built on camera, as a curriculum module, not silently as shelf-ware.

**Lesson:** pattern-matching to "best practice" architecture is a form of AI hallucination too —
the org-chart of a big warehouse imposed on a one-course platform. The consumer test
(who reads this model?) beats the pattern every time. Human simplicity instinct: 3, AI architecture: 0.

## Phase 6 — the dashboard puts the numbers on screen — 2026-07-28

**Task:** build the Evidence page for the core six on top of the published marts.

**What worked:** the marts held. Five of the six questions answered with columns that already
existed — no new modeling needed to draw them. Evidence's constraint (its DuckDB connector
autoloads only *default* extensions, so it cannot ATTACH a DuckLake) turned into a clean
boundary: `just publish` copies marts into a plain `dashboard.duckdb`. The dashboard reads a
snapshot, and the refresh is one word.

**What the screen exposed — the real value of the phase:**

1. **Outcome leakage.** `lessons_viewed` counts lessons at any time, including after payment.
   Plot it and the 7+ bucket is *entirely* PAID students — the "driver" of conversion turned out
   to be a consequence of it. A number that looked like an insight was a tautology.
2. **A grain trap avoided.** Q6 (revenue) does not belong in `mart_kpis_weekly`: payment week is
   not cohort week. New 8-line `mart_revenue_weekly` instead — built because a consumer finally
   asked for it, which is the rule.
3. **State vs state-at-the-time.** `access_type` flips to PAID on conversion, so "engaged FREE
   students who converted" is 0 by construction. Cohort on signup, never on current state.
4. **The engaged threshold settled itself.** The distribution has a plateau at 6 (the free module)
   and a gap to 13+. Engaged = ≥3 of the 6 free lessons — decided by looking, not by guessing.

**Where the AI went wrong:** it first shipped `just publish` as a multi-line escaped SQL string
inside the justfile — unreadable and fragile enough that Tom commented it out. Moved to
`infra/publish.sh`, same shape as `ducklake-setup.sh`. Shell belongs in shell files.

**Lesson:** a dashboard is not the end of modeling, it is the audit of it. Four modeling defects
were invisible in SQL review and obvious the moment a chart was drawn. Build the view early —
it interrogates the models better than any test.

### The dashboard got rejected, and that produced the skill — 2026-07-28

I built a page that answered all six questions: five KPIs, six sections, three tables,
a footer. Tom's verdict: *"the dashboard is bad, too long, not clear enough."* He was
right, and the failure mode was the same one as the over-modelling incident earlier in
the project — the AI adding volume where clarity was asked for. Comprehensiveness is
the easy thing to produce and the wrong thing to want.

The fix was not a better page. It was a **system**: `.claude/skills/evidence-dashboard/`,
which any Claude session opening this repo now loads automatically. Four files:

- `SKILL.md` — an eight-step procedure, a page budget (`index.md` = ≤5 KPIs, ≤3 charts,
  0 tables), and a definition-of-done checklist.
- `references/domain.md` — the frozen questions, the mart contracts with grains and
  column lists, the settled definitions, and seven traps in this data.
- `references/evidence-syntax.md` — component inventory and prop lists verified against
  the docs, not remembered. The rule written into it: *if a prop is not in this file,
  do not guess it.*
- `references/design-rules.md` — job→form table, series-count ladder, colour
  non-negotiables, anti-patterns.

Two things worth recording:

**The palette was wrong and nobody could have seen it by looking.** Running the
validator on `evidence.config.yaml` failed four of five checks — worst adjacent pair at
ΔE 4.6 under protanopia, and 7.3 even for normal vision against a hard floor of 15. Two
series on a chart were effectively the same colour for everyone. Replaced with a
measured palette that passes in both light and dark. Lesson: colour is computable, so
compute it.

**Verification found the real limit of the device VM.** No `duckdb` CLI, and the
`node_modules` duckdb binding is darwin-arm64 while the bridge VM is linux-arm64. So the
snapshot was staged into the cloud container and every query on the new pages was run
against it there. Result: index, growth and conversion queries all pass and return the
funnel we expect (683 → 97 → 54 → 7). The revenue queries could **not** be verified —
`mart_revenue_weekly` does not exist in the published snapshot yet, because
`just transform` + `just publish` have not run since the model was added.

**One finding the charts surfaced immediately:** `tik_tok` converts visits to signups at
9.4% against 16.0% for `other`. The bridge brings volume (277 visitors) and worse
intent. That is a Q2 answer that changes what to do next week, which is the whole test.
