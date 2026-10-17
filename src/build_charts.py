import sys
from pathlib import Path
 
import duckdb
import matplotlib
 
matplotlib.use("Agg")  # no window needed, we only save files
import matplotlib.pyplot as plt
 
DB_PATH = "data/chinook.duckdb"
OUT_DIR = Path("docs/img")
SOURCE_NOTE = "Source: Chinook sample database (github.com/lerocha/chinook-database)"
BAR_COLOR = "#2f6db5"
 
 
def finish(fig, ax, title: str, subtitle: str, filename: str) -> None:
    """Common styling, then save the figure to OUT_DIR/filename."""
    ax.spines[["top", "right"]].set_visible(False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.text(0.02, 0.965, title, fontsize=15, fontweight="bold", ha="left", va="top")
    fig.text(0.02, 0.915, subtitle, fontsize=10, color="#555555", ha="left", va="top")
    fig.text(0.02, 0.015, SOURCE_NOTE, fontsize=8, color="#777777", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 0.88))
    path = OUT_DIR / filename
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)
    print(f"saved {path}")
 
 
def revenue_by_year(con) -> None:
    df = con.sql("""
        SELECT invoice_year, revenue, revenue_yoy_pct, last_invoice_date
        FROM kpi_revenue_by_year ORDER BY invoice_year
    """).df()
    revenue = df["revenue"].astype(float)
 
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(df["invoice_year"].astype(str), revenue, color=BAR_COLOR, width=0.6)
    for x, (rev, yoy) in enumerate(zip(revenue, df["revenue_yoy_pct"])):
        label = f"{rev:,.0f}"
        if yoy == yoy:  # NaN != NaN, so this skips the first year (no prior year)
            label += f"\n({yoy:+.1f}% vs prior year)"
        ax.text(x, rev + revenue.max() * 0.015, label, ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, revenue.max() * 1.22)
    ax.set_ylabel("Revenue")
    ax.yaxis.grid(True, color="#e5e5e5")
    ax.set_axisbelow(True)
 
    last_date = str(df["last_invoice_date"].iloc[-1])[:10]
    finish(fig, ax,
           "Revenue per year",
           f"Change vs prior year in brackets. Data ends {last_date}, so the final year is not fully comparable.",
           "revenue_by_year.png")
 
 
def horizontal_bar_chart(df, name_col: str, title: str, subtitle: str, filename: str) -> None:
    """Horizontal bars, largest on top, labelled with revenue and share."""
    revenue = df["revenue"].astype(float)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.barh(df[name_col], revenue, color=BAR_COLOR, height=0.65)
    ax.invert_yaxis()
    for y, (rev, share) in enumerate(zip(revenue, df["revenue_share_pct"].astype(float))):
        ax.text(rev + revenue.max() * 0.01, y, f"{rev:,.0f}  ({share:.1f}%)",
                va="center", fontsize=9)
    ax.set_xlim(0, revenue.max() * 1.22)
    ax.set_xlabel("Revenue (share of total in brackets)")
    ax.xaxis.grid(True, color="#e5e5e5")
    ax.set_axisbelow(True)
    finish(fig, ax, title, subtitle, filename)
 
 
def revenue_by_genre(con) -> None:
    df = con.sql("""
        SELECT genre_name, revenue, revenue_share_pct
        FROM kpi_revenue_by_genre ORDER BY revenue_rank, genre_name LIMIT 10
    """).df()
    total_genres = con.sql("SELECT count(*) FROM kpi_revenue_by_genre").fetchone()[0]
    top_share = df["revenue_share_pct"].astype(float).sum()
    horizontal_bar_chart(
        df, "genre_name", "Revenue by genre (top 10)",
        f"Top 10 of {total_genres} genres with sales account for {top_share:.0f}% of revenue.",
        "revenue_by_genre.png")
 
 
def top_artists(con) -> None:
    df = con.sql("""
        SELECT artist_name, revenue, revenue_share_pct
        FROM kpi_revenue_by_artist ORDER BY revenue_rank, artist_name LIMIT 10
    """).df()
    total_artists = con.sql("SELECT count(*) FROM kpi_revenue_by_artist").fetchone()[0]
    top_share = df["revenue_share_pct"].astype(float).sum()
    horizontal_bar_chart(
        df, "artist_name", "Top 10 artists by revenue",
        f"Top 10 of {total_artists} artists with sales account for {top_share:.0f}% of revenue.",
        "top10_artists.png")
 
 
def main() -> int:
    if not Path(DB_PATH).exists():
        print(f"{DB_PATH} not found. Run: make load && make sql")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        revenue_by_year(con)
        revenue_by_genre(con)
        top_artists(con)
    except duckdb.CatalogException as err:
        print(f"A KPI view is missing. Run: make sql\n{err}")
        return 1
    finally:
        con.close()
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())