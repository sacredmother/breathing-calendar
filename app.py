# app.py

import calendar
from datetime import date

import pandas as pd
import streamlit as st


# ============================================================
# BREATHING CALENDAR
#
# Year = field.
# Month = octave.
# Day = pulse.
# Root = phase.
# Gate = return to One.
# ============================================================


# ---------- Core math ----------

def digital_root(n: int) -> int:
    """Return the 1-9 digital root."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    """Return the sum of the digits of an integer."""
    return sum(int(digit) for digit in str(abs(n)))


def year_root(year: int) -> int:
    """Return the digital root of a year."""
    return digital_root(digit_sum(year))


CANON_PAIRS = {
    "1/8": "Origin return",
    "2/7": "Water / Light mirror",
    "3/6": "Sun / Moon mirror",
    "4/5": "Girdle hinge",
    "5/4": "Hinge return",
    "6/3": "Moon / Sun mirror",
    "7/2": "Higher mirror",
    "8/1": "Outer return",
    "9/9": "Completion mirror",
}


def build_year_table(year: int) -> pd.DataFrame:
    """Build one row for every date in the selected year."""
    yr = year_root(year)
    rows = []

    for month in range(1, 13):
        month_root = digital_root(month)
        days_in_month = calendar.monthrange(year, month)[1]

        for day in range(1, days_in_month + 1):
            day_root = digital_root(day)
            raw_sum = yr + month_root + day_root
            date_root = digital_root(raw_sum)
            octave_pair = f"{month_root}/{day_root}"

            rows.append(
                {
                    "Date": date(year, month, day),
                    "Month": calendar.month_name[month],
                    "Month #": month,
                    "Day": day,
                    "Year Root": yr,
                    "Month Root": month_root,
                    "Day Root": day_root,
                    "Raw Sum": raw_sum,
                    "Date Root": date_root,
                    "Octave Pair": octave_pair,
                    "1-Gate": date_root == 1,
                    "Canon Pair": octave_pair in CANON_PAIRS,
                    "Canon Meaning": CANON_PAIRS.get(octave_pair, ""),
                    "Grammar": f"{month_root} + {day_root} + {yr} = {raw_sum} → {date_root}",
                }
            )

    return pd.DataFrame(rows)


# ---------- Visual cards ----------

def day_card(row: pd.Series) -> str:
    """Render one day as a readable HTML card."""
    day = row["Day"]
    date_root = row["Date Root"]
    day_root = row["Day Root"]
    pair = row["Octave Pair"]
    grammar = row["Grammar"]

    is_gate = bool(row["1-Gate"])
    is_canon = bool(row["Canon Pair"])

    background = "#ffffff"
    border = "1px solid #a8a8a8"

    if is_canon:
        background = "#eaf2ff"
        border = "2px solid #265ca8"

    if is_gate:
        background = "#fff0a6"
        border = "4px solid #111111"

    if is_gate and is_canon:
        background = "#ffe28a"
        border = "4px solid #111111"

    badges = ""

    if is_gate:
        badges += """
        <div style="
            display:inline-block;
            margin-top:8px;
            padding:3px 8px;
            border-radius:999px;
            background:#111111;
            color:#ffffff;
            font-size:11px;
            font-weight:900;
            letter-spacing:0.03em;
        ">
            GATE
        </div>
        """

    if is_canon:
        badges += f"""
        <div style="
            display:inline-block;
            margin-top:6px;
            padding:3px 8px;
            border-radius:999px;
            background:#265ca8;
            color:#ffffff;
            font-size:11px;
            font-weight:900;
            letter-spacing:0.01em;
        ">
            {row["Canon Meaning"]}
        </div>
        """

    return f"""
    <div style="
        border:{border};
        background:{background};
        border-radius:14px;
        padding:10px;
        min-height:150px;
        color:#111111;
        font-size:15px;
        line-height:1.35;
        box-sizing:border-box;
    ">
        <div style="font-size:28px;font-weight:900;line-height:1;">{day}</div>

        <div style="margin-top:8px;"><b>Date Root:</b> {date_root}</div>
        <div><b>Day Root:</b> {day_root}</div>
        <div><b>Pair:</b> {pair}</div>

        <div style="
            margin-top:8px;
            padding-top:6px;
            border-top:1px solid rgba(0,0,0,0.18);
            font-size:12px;
            font-weight:800;
        ">
            {grammar}
        </div>

        <div style="margin-top:4px;">
            {badges}
        </div>
    </div>
    """


def render_month(df: pd.DataFrame, year: int, month: int) -> None:
    """Render one month using native Streamlit columns."""
    month_name = calendar.month_name[month]
    month_root = digital_root(month)
    yr = year_root(year)

    st.markdown("---")
    st.markdown(f"## {month_name}")
    st.caption(f"Month Root {month_root} · Year Root {yr}")

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    header_cols = st.columns(7)
    for col, weekday in zip(header_cols, weekdays):
        col.markdown(
            f"""
            <div style="
                text-align:center;
                font-weight:900;
                color:#111111;
                border-bottom:2px solid #111111;
                padding-bottom:6px;
                margin-bottom:6px;
            ">
                {weekday}
            </div>
            """,
            unsafe_allow_html=True,
        )

    first_weekday, days_in_month = calendar.monthrange(year, month)
    month_df = df[df["Month #"] == month]

    current_day = 1

    # First week
    cols = st.columns(7)
    for i in range(7):
        if i < first_weekday:
            cols[i].markdown("&nbsp;", unsafe_allow_html=True)
        else:
            row = month_df[month_df["Day"] == current_day].iloc[0]
            cols[i].markdown(day_card(row), unsafe_allow_html=True)
            current_day += 1

    # Remaining weeks
    while current_day <= days_in_month:
        cols = st.columns(7)

        for i in range(7):
            if current_day <= days_in_month:
                row = month_df[month_df["Day"] == current_day].iloc[0]
                cols[i].markdown(day_card(row), unsafe_allow_html=True)
                current_day += 1
            else:
                cols[i].markdown("&nbsp;", unsafe_allow_html=True)


# ---------- Summaries ----------

def gate_summary(df: pd.DataFrame) -> pd.DataFrame:
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


# ---------- App ----------

st.set_page_config(
    page_title="Breathing Calendar",
    page_icon="🪶",
    layout="wide",
)

st.title("🪶 Breathing Calendar")

st.markdown(
    """
A living calendar-root calculator for date roots, octave pairs, 1-gates, and mirror-phase grammar.

**Year = field. Month = octave. Day = pulse. Root = phase. Gate = return to One.**
"""
)

with st.sidebar:
    st.header("Controls")

    selected_year = st.number_input(
        "Year",
        min_value=1,
        max_value=9999,
        value=2026,
        step=1,
    )

    display_mode = st.radio(
        "Display",
        [
            "Full Calendar",
            "Only 1-Gates",
            "Only Canon Pairs",
            "Table View",
            "Pair Summary",
        ],
    )

    months = st.multiselect(
        "Months",
        list(range(1, 13)),
        default=[1],
        format_func=lambda m: calendar.month_name[m],
    )

df = build_year_table(selected_year)

yr = year_root(selected_year)
gates = df[df["1-Gate"]]
canon = df[df["Canon Pair"]]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Year Root", yr)
col2.metric("Days", len(df))
col3.metric("1-Gates", len(gates))
col4.metric("Canon Pair Days", len(canon))

st.info(
    f"Date Root = digital_root(Year Root + Month Root + Day Root). "
    f"For {selected_year}: Date Root = digital_root({yr} + Month Root + Day Root)."
)

st.markdown(
    """
### Reading the Calendar

- **Date Root** = visible phase of the date
- **Day Root** = root of the day number
- **Pair** = Month Root / Day Root
- **Yellow** = 1-Gate / return to One
- **Blue** = canon octave-pair day
"""
)

if selected_year == 2026:
    st.success(
        "2026 has Year Root 1. The year supplies the One Light carrier. "
        "The date-field reveals octave-pair gates where month and day-root complete the 9-field."
    )

# ---------- Display modes ----------

if display_mode == "Full Calendar":
    for month in months:
        render_month(df, selected_year, month)

elif display_mode == "Only 1-Gates":
    st.subheader("1-Gates")

    st.dataframe(
        gates[
            [
                "Date",
                "Month",
                "Day",
                "Year Root",
                "Month Root",
                "Day Root",
                "Raw Sum",
                "Date Root",
                "Octave Pair",
                "Canon Meaning",
                "Grammar",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 1-Gates by Month")
    st.dataframe(
        gate_summary(df),
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Only Canon Pairs":
    st.subheader("Canon Octave Pair Days")

    st.dataframe(
        canon[
            [
                "Date",
                "Month",
                "Day",
                "Year Root",
                "Month Root",
                "Day Root",
                "Date Root",
                "Octave Pair",
                "1-Gate",
                "Canon Meaning",
                "Grammar",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Table View":
    st.subheader("Full Table")

    st.dataframe(
        df[
            [
                "Date",
                "Month",
                "Day",
                "Year Root",
                "Month Root",
                "Day Root",
                "Raw Sum",
                "Date Root",
                "Octave Pair",
                "1-Gate",
                "Canon Pair",
                "Canon Meaning",
                "Grammar",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Pair Summary":
    st.subheader("Octave Pair Summary")

    st.dataframe(
        pair_summary(df),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Canon Pair Key")

    key_rows = [
        {"Octave Pair": pair, "Meaning": meaning}
        for pair, meaning in CANON_PAIRS.items()
    ]

    st.dataframe(
        pd.DataFrame(key_rows),
        use_container_width=True,
        hide_index=True,
    )

# ---------- Download ----------

st.download_button(
    "Download full year CSV",
    data=df.to_csv(index=False),
    file_name=f"breathing_calendar_{selected_year}.csv",
    mime="text/csv",
)
