# app.py

import calendar
from datetime import date

import pandas as pd
import streamlit as st


# ============================================================
# LIVING CALENDAR ROOT CALCULATOR
# Occam's Razor Grammar:
#
# Year Root  = digital root of year
# Month Root = digital root of month
# Day Root   = digital root of day
#
# Date Root  = digital root(Year Root + Month Root + Day Root)
# Octave Pair = Month Root / Day Root
# 1-Gate      = Date Root == 1
#
# Year = field.
# Month = octave.
# Day = pulse.
# Root = phase.
# Gate = return to One.
# ============================================================


# ---------- Core Math ----------

def digital_root(n: int) -> int:
    """
    Returns the 1-9 digital root.
    Example:
    10 -> 1
    18 -> 9
    29 -> 2
    """
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    """Returns the sum of digits of an integer."""
    return sum(int(d) for d in str(abs(n)))


def year_root(year: int) -> int:
    """Digital root of the year digits."""
    return digital_root(digit_sum(year))


def build_year_table(year: int) -> pd.DataFrame:
    """
    Builds a full living calendar table for any year.
    Each row is one day.
    """
    yr_root = year_root(year)
    rows = []

    for month in range(1, 13):
        month_root = digital_root(month)
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]

        for day in range(1, days_in_month + 1):
            day_root = digital_root(day)
            raw_sum = yr_root + month_root + day_root
            date_root = digital_root(raw_sum)
            octave_pair = f"{month_root}/{day_root}"
            pair_sum = month_root + day_root
            pair_sum_root = digital_root(pair_sum)

            rows.append(
                {
                    "Date": date(year, month, day),
                    "Month": month_name,
                    "Month #": month,
                    "Day": day,
                    "Year Root": yr_root,
                    "Month Root": month_root,
                    "Day Root": day_root,
                    "Raw Sum": raw_sum,
                    "Date Root": date_root,
                    "Octave Pair": octave_pair,
                    "Pair Sum": pair_sum,
                    "Pair Sum Root": pair_sum_root,
                    "1-Gate": date_root == 1,
                    "Gate Grammar": (
                        f"{month_root} + {day_root} + {yr_root} = "
                        f"{raw_sum} → {date_root}"
                    ),
                }
            )

    return pd.DataFrame(rows)


def gate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes all 1-gates by month."""
    gates = df[df["1-Gate"]].copy()

    if gates.empty:
        return pd.DataFrame()

    summary = (
        gates.groupby(["Month #", "Month", "Month Root"])
        .agg(
            Gate_Days=("Day", lambda x: ", ".join(str(v) for v in x)),
            Gate_Day_Roots=("Day Root", lambda x: ", ".join(str(v) for v in sorted(set(x)))),
            Octave_Pairs=("Octave Pair", lambda x: ", ".join(x)),
            Gate_Count=("Day", "count"),
        )
        .reset_index()
        .sort_values("Month #")
    )

    return summary


def pair_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Counts octave-pair appearances across the year."""
    return (
        df.groupby(["Octave Pair", "Month Root", "Day Root"])
        .agg(
            Count=("Date", "count"),
            Gate_Count=("1-Gate", "sum"),
            First_Date=("Date", "min"),
            Last_Date=("Date", "max"),
        )
        .reset_index()
        .sort_values(["Month Root", "Day Root"])
    )


# ---------- Visual Helpers ----------

ROOT_LABELS = {
    1: "1 · Gate / Beginning",
    2: "2 · Mirror / Pair",
    3: "3 · Motion / Expression",
    4: "4 · Foundation / Hinge",
    5: "5 · Breath / Center",
    6: "6 · Harmony / Return",
    7: "7 · Crown / Mystery",
    8: "8 · Infinity / Mirror Loop",
    9: "9 · Completion / Womb",
}

OCTAVE_PAIR_LABELS = {
    "1/8": "O1/O8 · outer return",
    "8/1": "O8/O1 · reflected return",
    "2/7": "O2/O7 · water/light mirror",
    "7/2": "O7/O2 · light/water mirror",
    "3/6": "O3/O6 · sun/moon mirror",
    "6/3": "O6/O3 · moon/sun mirror",
    "4/5": "O4/O5 · girdle hinge",
    "5/4": "O5/O4 · hinge return",
    "9/9": "O9/O9 · completion reflecting itself",
}


def root_class(root: int) -> str:
    """CSS class for root value."""
    return f"root-{root}"


def render_month_card(df: pd.DataFrame, year: int, month: int) -> str:
    """
    Creates an HTML calendar card for one month.
    Each day shows:
    Day number
    Date root
    Octave pair
    """
    month_df = df[df["Month #"] == month].copy()
    month_name = calendar.month_name[month]
    month_root = digital_root(month)
    yr_root = year_root(year)

    first_weekday, days_in_month = calendar.monthrange(year, month)
    # Python calendar: Monday=0, Sunday=6

    html = f"""
    <div class="month-card">
        <div class="month-title">
            <div>{month_name}</div>
            <div class="month-subtitle">Month Root {month_root} · Year Root {yr_root}</div>
        </div>
        <div class="weekday-row">
            <div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>
        </div>
        <div class="calendar-grid">
    """

    for _ in range(first_weekday):
        html += '<div class="empty-day"></div>'

    for day in range(1, days_in_month + 1):
        row = month_df[month_df["Day"] == day].iloc[0]
        d_root = int(row["Date Root"])
        day_root = int(row["Day Root"])
        pair = row["Octave Pair"]
        is_gate = bool(row["1-Gate"])
        gate_class = " gate-day" if is_gate else ""
        known_pair_class = " known-pair" if pair in OCTAVE_PAIR_LABELS else ""

        html += f"""
        <div class="day-cell {root_class(d_root)}{gate_class}{known_pair_class}">
            <div class="day-number">{day}</div>
            <div class="date-root">DR {d_root}</div>
            <div class="pair">{pair}</div>
            <div class="day-root">day {day_root}</div>
        </div>
        """

    html += """
        </div>
    </div>
    """

    return html


def inject_css() -> None:
    """Adds clean visual styling."""
    st.markdown(
        """
        <style>
        .main {
            background: radial-gradient(circle at top, #fbf7ef 0%, #f5efe4 38%, #efe7da 100%);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1400px;
        }

        h1, h2, h3 {
            letter-spacing: -0.03em;
        }

        .hero {
            padding: 28px 30px;
            border-radius: 28px;
            background: rgba(255, 255, 255, 0.66);
            border: 1px solid rgba(90, 70, 40, 0.14);
            box-shadow: 0 18px 50px rgba(80, 60, 35, 0.10);
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 42px;
            font-weight: 750;
            line-height: 1.0;
            margin-bottom: 10px;
            color: #2d261c;
        }

        .hero-subtitle {
            font-size: 18px;
            color: #6b5a45;
            max-width: 900px;
        }

        .formula-box {
            padding: 18px 20px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(90, 70, 40, 0.12);
            margin: 12px 0;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            color: #3b3125;
        }

        .metric-card {
            padding: 18px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(90, 70, 40, 0.12);
            box-shadow: 0 8px 30px rgba(80, 60, 35, 0.07);
        }

        .month-card {
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(90, 70, 40, 0.14);
            border-radius: 26px;
            padding: 18px;
            margin-bottom: 26px;
            box-shadow: 0 14px 42px rgba(80, 60, 35, 0.09);
        }

        .month-title {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            font-size: 26px;
            font-weight: 750;
            color: #2d261c;
            margin-bottom: 12px;
        }

        .month-subtitle {
            font-size: 14px;
            font-weight: 500;
            color: #77634d;
        }

        .weekday-row {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-bottom: 8px;
            color: #7a6650;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
        }

        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }

        .empty-day {
            min-height: 88px;
            border-radius: 16px;
            background: rgba(255,255,255,0.25);
        }

        .day-cell {
            min-height: 88px;
            border-radius: 18px;
            padding: 9px 10px;
            border: 1px solid rgba(40, 30, 20, 0.08);
            position: relative;
            overflow: hidden;
        }

        .day-number {
            font-size: 18px;
            font-weight: 800;
            color: #2d261c;
        }

        .date-root {
            font-size: 13px;
            font-weight: 800;
            margin-top: 4px;
            color: #2d261c;
        }

        .pair {
            font-size: 12px;
            margin-top: 2px;
            color: #4d4234;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }

        .day-root {
            font-size: 11px;
            color: #7a6650;
        }

        .gate-day {
            outline: 3px solid rgba(45, 38, 28, 0.45);
            box-shadow: inset 0 0 0 2px rgba(255,255,255,0.55), 0 8px 20px rgba(80,60,35,0.14);
        }

        .gate-day::after {
            content: "GATE";
            position: absolute;
            right: -26px;
            top: 12px;
            transform: rotate(35deg);
            background: rgba(45, 38, 28, 0.78);
            color: white;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 28px;
            letter-spacing: 0.06em;
        }

        .known-pair {
            border-style: solid;
            border-width: 2px;
        }

        .root-1 { background: rgba(255, 250, 224, 0.95); }
        .root-2 { background: rgba(239, 246, 255, 0.95); }
        .root-3 { background: rgba(240, 253, 244, 0.95); }
        .root-4 { background: rgba(250, 245, 255, 0.95); }
        .root-5 { background: rgba(255, 247, 237, 0.95); }
        .root-6 { background: rgba(236, 253, 245, 0.95); }
        .root-7 { background: rgba(245, 243, 255, 0.95); }
        .root-8 { background: rgba(255, 241, 242, 0.95); }
        .root-9 { background: rgba(248, 250, 252, 0.95); }

        .legend-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-top: 10px;
        }

        .legend-item {
            border-radius: 16px;
            padding: 10px 12px;
            border: 1px solid rgba(90, 70, 40, 0.12);
            font-size: 14px;
            font-weight: 650;
        }

        .pair-pill {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            margin: 4px 4px 4px 0;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(90, 70, 40, 0.15);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
        }

        @media (max-width: 900px) {
            .calendar-grid, .weekday-row {
                gap: 5px;
            }

            .day-cell, .empty-day {
                min-height: 76px;
                padding: 7px;
            }

            .hero-title {
                font-size: 32px;
            }

            .month-title {
                font-size: 22px;
                flex-direction: column;
                gap: 2px;
            }

            .legend-grid {
                grid-template-columns: repeat(1, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_dataframe(df: pd.DataFrame):
    """Simple dataframe styling for gates and roots."""
    def highlight_gate(row):
        if "1-Gate" in row and row["1-Gate"] is True:
            return ["background-color: #fff3bf; font-weight: 700"] * len(row)
        return [""] * len(row)

    return df.style.apply(highlight_gate, axis=1)


# ---------- Streamlit App ----------

st.set_page_config(
    page_title="Living Calendar Root Calculator",
    page_icon="🪶",
    layout="wide",
)

inject_css()

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Living Calendar Root Calculator</div>
        <div class="hero-subtitle">
            A simple phase-display engine for year root, month root, day root,
            date root, octave-pair grammar, and 1-gates.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Calendar Field")

    selected_year = st.number_input(
        "Enter year",
        min_value=1,
        max_value=9999,
        value=2026,
        step=1,
    )

    show_months = st.multiselect(
        "Months to display",
        options=list(range(1, 13)),
        default=list(range(1, 13)),
        format_func=lambda m: calendar.month_name[m],
    )

    st.divider()

    st.subheader("Filters")
    show_gates_only = st.checkbox("Table: show only 1-gates", value=False)
    show_known_pairs_only = st.checkbox("Table: show only octave-pair canon", value=False)

    st.divider()

    st.subheader("Occam’s Razor")
    st.caption("Year = field")
    st.caption("Month = octave")
    st.caption("Day = pulse")
    st.caption("Root = phase")
    st.caption("Gate = return to One")


df = build_year_table(selected_year)
yr = year_root(selected_year)
gates = df[df["1-Gate"]].copy()
known_pair_df = df[df["Octave Pair"].isin(OCTAVE_PAIR_LABELS.keys())].copy()

# ---------- Top Metrics ----------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Year Root", yr)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Days", len(df))
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("1-Gates", len(gates))
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Canon Pair Days", len(known_pair_df))
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    f"""
    <div class="formula-box">
    Date Root = digital_root(Year Root + Month Root + Day Root)<br>
    For {selected_year}: Date Root = digital_root({yr} + Month Root + Day Root)
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Tabs ----------

tab_calendar, tab_gates, tab_pairs, tab_table, tab_legend = st.tabs(
    [
        "Living Calendar",
        "1-Gates",
        "Octave Pairs",
        "Full Table",
        "Grammar",
    ]
)


# ---------- Living Calendar ----------

with tab_calendar:
    st.subheader(f"{selected_year} Living Calendar")

    for month in show_months:
        st.markdown(
            render_month_card(df, selected_year, month),
            unsafe_allow_html=True,
        )


# ---------- Gates ----------

with tab_gates:
    st.subheader("1-Gates")

    st.markdown(
        """
        A 1-gate opens when the full date resolves to One.
        The visible grammar is:
        """
    )

    st.markdown(
        """
        <div class="formula-box">
        Month Root + Day Root + Year Root → 1
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary = gate_summary(df)

    if summary.empty:
        st.info("No 1-gates found. This should be rare with this grammar.")
    else:
        st.dataframe(summary, use_container_width=True, hide_index=True)

    st.download_button(
        "Download 1-gates as CSV",
        data=gates.to_csv(index=False),
        file_name=f"one_gates_{selected_year}.csv",
        mime="text/csv",
    )

    st.markdown("### Gate Detail")

    gate_cols = [
        "Date",
        "Month",
        "Day",
        "Month Root",
        "Day Root",
        "Year Root",
        "Raw Sum",
        "Date Root",
        "Octave Pair",
        "Gate Grammar",
    ]

    st.dataframe(
        gates[gate_cols],
        use_container_width=True,
        hide_index=True,
    )


# ---------- Octave Pairs ----------

with tab_pairs:
    st.subheader("Octave-Pair Grammar")

    st.markdown(
        """
        The octave pair is the month root over the day root.
        These are the canon pairings we have been watching:
        """
    )

    pills = ""
    for pair, label in OCTAVE_PAIR_LABELS.items():
        pills += f'<span class="pair-pill">{pair} · {label}</span>'

    st.markdown(pills, unsafe_allow_html=True)

    st.markdown("### Pair Summary")

    ps = pair_summary(df)
    st.dataframe(ps, use_container_width=True, hide_index=True)

    st.markdown("### Canon Pair Days")

    canon_cols = [
        "Date",
        "Month",
        "Day",
        "Month Root",
        "Day Root",
        "Year Root",
        "Date Root",
        "Octave Pair",
        "1-Gate",
        "Gate Grammar",
    ]

    st.dataframe(
        known_pair_df[canon_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download canon pair days as CSV",
        data=known_pair_df.to_csv(index=False),
        file_name=f"canon_octave_pairs_{selected_year}.csv",
        mime="text/csv",
    )


# ---------- Full Table ----------

with tab_table:
    st.subheader("Full Year Table")

    table_df = df.copy()

    if show_gates_only:
        table_df = table_df[table_df["1-Gate"]]

    if show_known_pairs_only:
        table_df = table_df[table_df["Octave Pair"].isin(OCTAVE_PAIR_LABELS.keys())]

    display_cols = [
        "Date",
        "Month",
        "Day",
        "Year Root",
        "Month Root",
        "Day Root",
        "Raw Sum",
        "Date Root",
        "Octave Pair",
        "Pair Sum",
        "Pair Sum Root",
        "1-Gate",
        "Gate Grammar",
    ]

    st.dataframe(
        style_dataframe(table_df[display_cols]),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download full year as CSV",
        data=df.to_csv(index=False),
        file_name=f"living_calendar_roots_{selected_year}.csv",
        mime="text/csv",
    )


# ---------- Grammar ----------

with tab_legend:
    st.subheader("Root Legend")

    legend_html = '<div class="legend-grid">'
    for root, label in ROOT_LABELS.items():
        legend_html += f'<div class="legend-item root-{root}">{label}</div>'
    legend_html += "</div>"

    st.markdown(legend_html, unsafe_allow_html=True)

    st.markdown("### Core Grammar")

    st.markdown(
        """
        <div class="formula-box">
        Year Root = digital_root(year)<br>
        Month Root = digital_root(month)<br>
        Day Root = digital_root(day)<br><br>
        Date Root = digital_root(Year Root + Month Root + Day Root)<br>
        Octave Pair = Month Root / Day Root<br>
        1-Gate = Date Root == 1
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### LOVE Table Read")

    st.markdown(
        """
        **Year = field**  
        **Month = octave**  
        **Day = pulse**  
        **Root = phase**  
        **Gate = return to One**

        The calculator does not treat the calendar as a flat line.
        It treats the date as a living phase expression.

        The year supplies the background field.  
        The month supplies the octave offset.  
        The day supplies the moving pulse.  
        The date root reveals the visible phase.  
        The 1-gate reveals the return to Source.
        """
    )

    st.markdown("### 2026 Key")

    if selected_year == 2026:
        st.success(
            "For 2026, the Year Root is 1. "
            "So every date is digital_root(1 + Month Root + Day Root). "
            "This is why the octave pairings reveal themselves so cleanly."
        )
    else:
        st.info(
            f"For {selected_year}, the Year Root is {yr}. "
            "The same grammar applies, but the gate pattern shifts."
        )
