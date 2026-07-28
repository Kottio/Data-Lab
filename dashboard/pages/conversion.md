---
title: Conversion — the free tier and the money
hide_header: true
---

[← overview](/) &nbsp;·&nbsp; [growth →](/growth)

How alive the free tier is (Q5) and what the money is doing (Q6). Q4 — _what makes an
engaged free user convert_ — is the one the business most wants and the one this data
cannot yet answer honestly; the last section says why.

```sql engagement
select
    count(*)                                    as free_students,
    count(*) filter (where lessons_viewed >= 3) as engaged,
    count(*) filter (where lessons_viewed = 0)  as never_activated,
    avg(lessons_viewed)                         as avg_lessons,
    avg(dash_access)                            as avg_dashboard_visits
from lake.drivers
where not converted
```

```sql free_depth
select
    least(lessons_viewed, 6) as free_lessons_opened,
    count(*)                 as students
from lake.drivers
where not converted
group by 1
order by 1
```

```sql revenue_weekly
select payment_week, payments, paying_students, revenue
from lake.revenue
order by payment_week
```

<Grid cols=5 gapSize=sm>
<BigValue data={engagement} value=free_students title="Free students" fmt=num0/>
<BigValue data={engagement} value=engaged title="Engaged (≥3 lessons)" fmt=num0/>
<BigValue data={engagement} value=never_activated title="Never opened a lesson" fmt=num0/>
<BigValue data={engagement} value=avg_lessons title="Avg lessons opened" fmt=num1/>
<BigValue data={engagement} value=avg_dashboard_visits title="Avg dashboard visits" fmt=num1/>
</Grid>

<!-- <Grid cols=2> -->

<BarChart
    data={free_depth}
    x=free_lessons_opened
    y=students
    sort=false
    title="Q5 · How deep does the free tier go?"
    subtitle="Non-payers only. The 0 bar is the never-activated group — the biggest block, and the cheapest to move."
    xAxisTitle="free lessons opened"
    yAxisTitle="students"
    chartAreaHeight=220
    labels=true
/>

<BarChart
    data={revenue_weekly}
    x=payment_week
    y=revenue
    yFmt='€#,##0'
    title="Q6 · Revenue, weekly"
    subtitle="Weeks with no payment have no row — the axis has holes, not zeros."
    yAxisTitle="revenue"
    chartAreaHeight=220
    labels=true
/>

<!-- </Grid> -->

<Details title="The payment weeks">

<DataTable data={revenue_weekly} rows=20 totalRow=true>
    <Column id=payment_week fmt="yyyy-mm-dd"/>
    <Column id=payments/>
    <Column id=paying_students/>
    <Column id=revenue fmt='€#,##0.00'/>
</DataTable>

</Details>

<Details title="Q4 · Why this page does not chart “what makes people convert”">

Three things block it, and each would make the chart lie:

1. **Outcome leakage.** `lessons_viewed` counts every lesson ever opened, including the
   paid ones opened _after_ paying. Plotting conversion against lesson depth would show
   a beautiful upward curve meaning only "people who bought the course read the course."
2. **`access_type` is current state.** A student who converts flips to PAID, so "engaged
   FREE students who converted" is zero by construction. Cohort on `signed_up_at`.
3. **n = 7.** Seven payers cannot support a rate split by source, week or depth.

The fix is a `lessons_before_payment` measure — lessons opened strictly before
`first_payment_at`. Until that exists this page says nothing rather than something false.

One student sits in the 6 bar of the depth chart with more than 6 lessons opened: the
comped access, PAID with no payment row.

</Details>
