"""DBuilders analytics — MCP server (v1).

Reads the published marts snapshot (dashboard.duckdb), never the live lake:
read-only, no lock exposure, marts-only by construction.
Refreshed by `just publish` / the daily 18:40 run.
"""

from pathlib import Path

import duckdb
from mcp.server.mcpserver import MCPServer      # ← était: from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).parent.parent
VITRINE = REPO_ROOT / "dashboard" / "sources" / "lake" / "dashboard.duckdb"

mcp = MCPServer("dbuilders-analytics")


@mcp.tool()
def revenue_weekly(last_n_weeks: int = 8) -> list[dict]:
    """Weekly revenue of the DBuilders course platform.

    One row per payment week (Monday-start), most recent first:
      payment_week    - week start date
      payments        - number of payments that week
      paying_students - distinct students who paid
      revenue         - gross revenue in EUR

    Caveat: amounts are assumed to be cents at the source - treat absolute revenue as provisional.
    Data is a daily snapshot, not live.
    """
    with duckdb.connect(str(VITRINE), read_only=True) as con:
        cur = con.execute(
            """
            select cast(payment_week as date) as payment_week,
                   payments, paying_students, revenue
            from mart_revenue_weekly
            order by payment_week desc
            limit ?
            """,
            [last_n_weeks],
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

@mcp.tool()
def traffic_weekly(last_n_weeks: int = 8) -> list[dict]:
    """Weekly acquisition traffic of the DBuilders course platform.

    TWO rows per cohort week (Monday-start), one per acquisition source:
      cohort_week     - week of the visitor's FIRST visit (cohort, not activity)
      source          - 'tik_tok' (came through the TikTok bridge link) or 'other'
      new_visitors    - first-time visitors that week
      signups         - how many of them created an account
      signup_rate_pct - signups / new_visitors, in percent

    Note: a week's numbers never change afterwards (cohort grain) -
    comparing weeks IS comparing acquisition performance.
    Data is a daily snapshot, not live.
    """
    with duckdb.connect(str(VITRINE), read_only=True) as con:
        cur = con.execute(
            """
            select cast(cohort_week as date) as cohort_week,
                   source, new_visitors, signups, signup_rate_pct
            from mart_kpis_weekly
            order by cohort_week desc, source
            limit ?
            """,
            [last_n_weeks * 2],   # 2 rows per week (one per source)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


if __name__ == "__main__":
    mcp.run(transport="stdio")   