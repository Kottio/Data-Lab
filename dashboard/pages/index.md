---
title: KottioDev
# full_width: true
hide_header: true
---

```sql funnel
select
    (select sum(new_visitors) from lake.kpis)                       as visitors,
    (select count(*) from lake.drivers)                             as signups,
    (select count(*) filter (where is_activated) from lake.drivers) as activated,
    (select count(*) filter (where converted) from lake.drivers)    as paying,
    (select coalesce(sum(revenue), 0) from lake.revenue)            as revenue
```

```sql headline
select
    *,
    signups::double   / nullif(visitors, 0)  as signup_rate,
    activated::double / nullif(signups, 0)   as activation_rate,
    paying::double    / nullif(activated, 0) as conversion_rate,
    revenue           / nullif(paying, 0)    as revenue_per_payer
from ${funnel}
```

```sql weekly
select cohort_week, source, new_visitors, signups
from lake.kpis
order by cohort_week
```

```sql revenue_weekly
select payment_week, revenue, payments
from lake.revenue
order by payment_week
```

<!-- <Grid cols=5 gapSize=sm> -->

<BigValue data={headline} value=visitors title="Visitors" fmt=num0/>

<BigValue data={headline} value=signups title="Signups" fmt=num0
  comparison=signup_rate comparisonTitle="of visitors" comparisonFmt=pct1 comparisonDelta=false/>

<BigValue data={headline} value=activated title="Opened a lesson" fmt=num0
  comparison=activation_rate comparisonTitle="of signups" comparisonFmt=pct1 comparisonDelta=false/>

<BigValue data={headline} value=paying title="Paying" fmt=num0
  comparison=conversion_rate comparisonTitle="of activated" comparisonFmt=pct1 comparisonDelta=false/>

<BigValue data={headline} value=revenue title="Revenue" fmt='€#,##0'
  comparison=revenue_per_payer comparisonTitle="per payer" comparisonFmt='€#,##0' comparisonDelta=false/>

<!-- </Grid> -->

Wide at the top, needle-thin at the bottom. The narrowest step is the one to work on.

<!-- <Grid cols=2> -->

<BarChart
    data={weekly}
    x=cohort_week
    y=signups
    series=source
    type=grouped
    title="Are new people arriving — and from where?"
    subtitle="Signups per week by source. The bridge is working if tik_tok outgrows other."
    yAxisTitle="signups"
    chartAreaHeight=220
/>

<BarChart
    data={revenue_weekly}
    x=payment_week
    y=revenue
    yFmt='€#,##0'
    title="Is money coming in?"
    subtitle="Weeks with no payment do not draw — the gaps are real, not missing data."
    yAxisTitle="revenue"
    chartAreaHeight=220
/>

<!-- </Grid> -->

[Acquisition and activation detail →](/growth) &nbsp;·&nbsp; [Free tier and conversion detail →](/conversion)

<Details title="How to read this honestly">

- **This is a snapshot.** The page reads `dashboard.duckdb`, refreshed by `just publish` —
  not the live lake.
- **n is tiny.** 7 payers. Every rate below the signup step moves by whole percentage
  points when one person acts. Read direction, never precision.
- **The funnel mixes two grains.** Visitors come from sessions, signups onward from
  students. Sessions that never stitched to a student are counted as visitors only.
- **Revenue assumes `amount` is in cents.** Not yet confirmed against Stripe.
- **Why there is no "what makes people convert" chart:** lesson counts include lessons
  read _after_ paying, so depth predicts nothing until `lessons_before_payment` exists.
  Saying nothing is better than charting a circular argument.

</Details>
