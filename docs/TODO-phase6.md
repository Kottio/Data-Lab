# TODO — closing Phase 6

> **Temporary file. Delete it when the three items below are done** (they get folded
> into `docs/Notes/Cleaned_Notes.md` and `docs/build-plan.md`, not kept here).

---

## 1. dbt test — make the tests actually run

Today **no test ever executes**: `just transform` has an empty body, and the
`dbt run --project-dir transform` line sits inside the `dashboard:` recipe.

**a. Fix the justfile** (`justfile`, lines 30–36) — the recipe is currently:

```
dashboard:
    cd dashboard && npm run sources && npm run dev
    dbt run --project-dir transform

transform:
transform-debug:
    dbt debug --project-dir transform
```

should be:

```
dashboard:
    cd dashboard && npm run sources && npm run dev

transform:
    dbt build --project-dir transform

transform-debug:
    dbt debug --project-dir transform
```

`dbt build` = `run` + `test`, model by model: a model whose test fails does not
propagate downstream. `dbt run` skips tests entirely.

**b. Cover the models that have no entry** — `transform/models/schema.yml` describes
4 models. Missing: `mart_kpis_weekly` and the 5 staging models. Keys to declare:

| model | key | tests |
|---|---|---|
| `stg_students` | `student_id` | unique, not_null |
| `stg_enrollments` | `enrollment_id` | unique, not_null |
| `stg_payments` | `payment_id` | unique, not_null |
| `stg_progress` | `progress_id` | unique, not_null |
| `stg_events` | `event_id` | unique, not_null |

Plus on `stg_payments.student_id`:

```yaml
        tests:
          - relationships: { to: ref('stg_students'), field: student_id }
```

Plus on `dim_student.acquisition_source` (the CASE has exactly three outcomes):

```yaml
        tests:
          - accepted_values:
              values: ['tik_tok', 'other', 'unknown']
```

**c. Two singular tests** — `mart_kpis_weekly` has a composite grain
(`cohort_week × source`), which `unique` cannot express and `dbt_utils` is not
installed. A singular test is a `.sql` file that passes when it returns zero rows.
Create `transform/tests/` (default `test-paths`, nothing to configure):

`transform/tests/assert_kpis_weekly_grain.sql`
```sql
select cohort_week, source, count(*)
from {{ ref('mart_kpis_weekly') }}
group by 1, 2
having count(*) > 1
```

`transform/tests/assert_known_paid_gap.sql`
```sql
-- KNOWN: access_type is current state; converted requires a payment row.
-- Exactly one student is PAID without a payment (manual grant). Fails if that changes.
select count(*)
from {{ ref('mart_conversion_drivers') }}
where access_type = 'PAID' and not converted
having count(*) <> 1
```

**Done when** `just transform` runs models *and* tests, and the run is green.

---

## 2. `event.properties` — emails in the payload

`ingestion/postgres_dlt.py` has **no PII transform at all** (43 lines, only
`apply_hints`). The emails are inside the JSON `properties` column of `event`, so
they travel raw into the lake and into `stg_events.properties`.

Blocking before anything is public.

- Add an `add_map` on `source.event` that walks `properties` and, for every key that
  holds an email (or a name), replaces the value with a salted hash — or drops the
  key. Allowlist beats blocklist here: keep the keys the analytics need, hash/drop
  the rest.
- Salt lives in `.env` (gitignored), never in the script.
- Then `just rebuild` — the lake is nuked and re-ingested, because a PII policy
  change does not apply retroactively to Parquet already written.
- Check the same question for `students` (`user_id` is a FK, fine — but confirm no
  name/email column was pulled).

**Done when** a query on `stg_events.properties` returns zero `@` characters.

---

## 3. git cleaning

`git rm -r --cached` on the old `Notes/` paths is **already done** — `git ls-files`
returns no notes file, and `.gitignore` carries `**/Notes/` and `Notetaking.md`.
What remains is the working tree.

Current `git status`:

```
 D .claude/skills/evidence-dashboard/references/domain.md   (moved to docs/domain.md)
 M justfile
 M setup-server.sh
 M transform/models/marts/dim_student.sql
 D transform/models/staging/stg_enrollements.sql            (rename → stg_enrollments)
?? .claude/settings.local.json
?? docs/domain.md
?? transform/models/staging/stg_enrollments.sql
```

- Decide on `.claude/settings.local.json` — local machine state, belongs in
  `.gitignore` rather than in the repo.
- Then commit the harvest. Suggested split (**you run these, not me**):

```bash
git add transform/models/staging/stg_enrollments.sql
git rm --cached transform/models/staging/stg_enrollements.sql
git add transform/models/marts/dim_student.sql
git commit -m "fix(transform): rename stg_enrollements -> stg_enrollments"

git add docs/domain.md .claude/skills/evidence-dashboard/references/domain.md
git commit -m "docs: move domain knowledge out of the evidence skill, project-level"

git add justfile setup-server.sh
git commit -m "chore: justfile recipes (transform runs dbt build)"
```

- **Rotate the `analytics_ro` password** — it transited chat and shell history.
  Neon console → reset the role's password → update `.env` and `.dlt/secrets.toml`.
  Not a git action, but it belongs to the same cleanup and it is the one with a
  real blast radius.

**Done when** `git status` is clean and the password is rotated.
