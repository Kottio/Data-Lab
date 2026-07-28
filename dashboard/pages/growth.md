---
title: Growth — acquisition and activation
hide_header: true
---

[← overview](/) &nbsp;·&nbsp; [conversion →](/conversion)

How many new people arrive (Q1), whether the bridge turns them into signups (Q2),
and whether onboarding catches them in the first week (Q3).

```sql weekly
select
    cohort_week,
    source,
    new_visitors,
    signups,
    signup_rate_pct / 100.0 as signup_rate
from lake.kpis
order by cohort_week, source
```

```sql by_source
select
    source,
    sum(new_visitors)                              as visitors,
    sum(signups)                                   as signups,
    sum(signups)::double / nullif(sum(new_visitors), 0) as signup_rate
from lake.kpis
group by 1
order by visitors desc
```

```sql activation
select
    date_trunc('week', signed_up_at)            as signup_week,
    count(*)                                    as signups,
    count(*) filter (where activated_within_7d) as activated_7d,
    count(*) filter (where activated_within_7d)::double
        / nullif(count(*), 0)                   as activation_rate
from lake.drivers
group by 1
order by 1
```

<!-- <Grid cols=2> -->

<BarChart
    data={weekly}
    x=cohort_week
    y=new_visitors
    series=source
    type=grouped
    title="Q1 · Visitors, weekly"
    subtitle="Top of the funnel — the number a video moves."
    yAxisTitle="visitors"
    chartAreaHeight=220
/>

<LineChart
    data={weekly}
    x=cohort_week
    y=signup_rate
    series=source
    yFmt=pct1
    markers=true
    title="Q2 · Visit → signup rate, by source"
    subtitle="Check the counts before believing a spike — a 100% week can be one visitor."
    yAxisTitle="signup rate"
    chartAreaHeight=220
/>

<!-- </Grid> -->

<Grid cols=2>

<BarChart
    data={by_source}
    x=source
    y=signup_rate
    yFmt=pct1
    title="Q2 · The whole picture, by source"
    subtitle="Volume and intent are not the same thing. Compare against the visitor counts."
    yAxisTitle="signup rate"
    chartAreaHeight=220
    labels=true
/>

<BarChart
    data={activation}
    x=signup_week
    y=activation_rate
    yFmt=pct1
    title="Q3 · Opened a lesson within 7 days"
    subtitle="A falling rate against rising signups means the top of the funnel is louder than the product."
    yAxisTitle="activated within 7 days"
    chartAreaHeight=220
/>

</Grid>

<Details title="The weekly numbers">

<Grid cols=2>

<DataTable data={weekly} rows=12 title="Traffic and signups">
    <Column id=cohort_week fmt="yyyy-mm-dd"/>
    <Column id=source/>
    <Column id=new_visitors/>
    <Column id=signups/>
    <Column id=signup_rate fmt=pct1/>
</DataTable>

<DataTable data={activation} rows=12 title="Activation">
    <Column id=signup_week fmt="yyyy-mm-dd"/>
    <Column id=signups/>
    <Column id=activated_7d/>
    <Column id=activation_rate fmt=pct1/>
</DataTable>

</Grid>

</Details>

<Details title="Caveats on this page">

- **Two different weeks.** Q1/Q2 cohort on _first sight_ (sessions); Q3 cohorts on
  _signup date_ (students). Never read them as one series.
- **`unknown` source** means the session never stitched to a student — those visitors
  are counted, their signups may not be.
- **`progress` is a state table.** "Opened a lesson" means _ever_ opened; revisits are
  overwritten upstream, so this is a floor, not a measure of activity.

</Details>
