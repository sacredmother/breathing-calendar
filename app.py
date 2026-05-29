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


def digital_root(n: int) -> int:
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def year_root(year: int) -> int:
    return digital_root(digit_sum(year))


CANON_PAIRS = {
    "4/5": "Girdle hinge",
    "5/4": "Hinge return",
    "6/3": "Moon/Sun mirror",
    "7/2": "Higher mirror",
    "8/1": "Outer return",
    "9/9": "Completion mirror",
    "1/8": "Origin return",
    "2/7": "Water/light mirror",
    "3/6": "Sun/moon mirror",
}


def build_year_table(year: int) -> pd.DataFrame:
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


def day_card(row):
    day = row["Day"]
    dr = row["Date Root"]
    day_root = row["Day Root"]
    pair = row["Octave Pair"]
    grammar = row["Grammar"]

    badges = []

    if row["1-Gate"]:
        badges.append("🟡 1-GATE")

    if row["Canon Pair"]:
        badges.append(f"🔵 {row['Canon Meaning']}")

    badge_text = "<br>".join(badges)

    border = "4px solid #111" if row["1-Gate"] else "1px solid #999"
    background = "#fff2a8" if row["1-Gate"] else "#ffffff"

    if row["Canon Pair"] and not row["1-Gate"]:
        background = "#e7f0ff"

    return f"""
    <div style="
        border:{border};
        background:{background};
        border-radius:14px;
        padding:10px;
        min-height:140px;
        color:#111;
        font-size:15px;
        line-height:1.35;
    ">
        <div style="font-size:26px;font-weight:900;">{day}</div>
        <div><b>Date Root:</b> {dr}</div>
        <div><b>Day Root:</b> {day_root}</div>
        <div><b>Pair:</b> {pair}</div>
        <div style="font-size:13px;margin-top:4px;"><b>{grammar}</b></div>
        <div style="margin-top:8px;font-size:13px;font-weight:800;">{badge_text}</div>
    </div>
    """


def render_month_native(df: pd.DataFrame, year: int, month: int):
    month_name = calendar.month_name[month]
    month_root = digital_root(month)
    yr = year_root(year)

    st.markdown("---")
    st.subheader(f"{month_name}")
    st.caption(f"Month Root {month_root} · Year Root {yr}")

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    header_cols = st.columns(7)
    for col, weekday in zip(header_cols, weekdays):
        col.markdown(f"**{weekday}**")

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


st.set_page_config(
    page_title="Breathing Calendar",
    page_icon="🪶",
    layout="wide",
)

st.title("🪶 Breathing Calendar")

st.markdown(
    """
**A living calendar-root calculator for date roots, octave pairs, 1-gates, and mirror-phase grammar.**

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
        ["Full Calendar", "Only 1-Gates", "Only Canon Pairs", "Table View"],
    )

    months = st.multiselect(
        "Months",
        list(range(1, 13)),
        default=list(range(1, 13)),
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

if display_mode == "Full Calendar":
    for month in months:
        render_month_native(df, selected_year, month)

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

else:
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

st.download_button(
    "Download full year CSV",
    data=df.to_csv(index=False),
    file_name=f"breathing_calendar_{selected_year}.csv",
    mime="text/csv",
)
