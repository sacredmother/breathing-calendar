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
    """Return 1-9 digital root."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def year_root(year: int) -> int:
    return digital_root(digit_sum(year))


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
                    "Grammar": f"{month_root} + {day_root} + {yr} = {raw_sum} → {date_root}",
                }
            )

    return pd.DataFrame(rows)


CANON_PAIRS = {
    "4/5": "Girdle hinge",
    "5/4": "Hinge return",
    "6/3": "Moon/Sun mirror",
    "7/2": "Higher mirror",
    "8/1": "Outer return",
    "9/9": "Completion mirror",
}


def inject_css():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
        }

        .hero {
            padding: 28px;
            border: 2px solid #222;
            border-radius: 18px;
            background: #ffffff;
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 42px;
            line-height: 1.05;
            font-weight: 800;
            color: #111111;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 19px;
            color: #333333;
            max-width: 900px;
        }

        .formula {
            padding: 16px 18px;
            border: 2px solid #222;
            border-radius: 14px;
            background: #f7f7f7;
            color: #111111;
            font-size: 18px;
            font-weight: 700;
            margin: 18px 0;
        }

        .month-box {
            border: 2px solid #222;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 24px;
            background: #ffffff;
        }

        .month-title {
            font-size: 28px;
            font-weight: 800;
            color: #111111;
            margin-bottom: 4px;
        }

        .month-subtitle {
            font-size: 16px;
            font-weight: 600;
            color: #444444;
            margin-bottom: 14px;
        }

        .day-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }

        .weekday {
            font-weight: 800;
            color: #111111;
            text-align: center;
            padding: 8px 0;
            border-bottom: 2px solid #222;
        }

        .blank {
            min-height: 96px;
            background: #eeeeee;
            border-radius: 10px;
        }

        .day {
            min-height: 96px;
            border: 2px solid #555;
            border-radius: 10px;
            padding: 8px;
            background: #ffffff;
            color: #111111;
        }

        .gate {
            background: #fff2a8;
            border: 4px solid #111111;
        }

        .canon {
            background: #e7f0ff;
        }

        .gate.canon {
            background: #ffe08a;
        }

        .day-number {
            font-size: 21px;
            font-weight: 900;
            color: #111111;
        }

        .day-line {
            font-size: 14px;
            font-weight: 700;
            color: #111111;
            margin-top: 3px;
        }

        .gate-label {
            display: inline-block;
            margin-top: 6px;
            padding: 3px 7px;
            border-radius: 999px;
            background: #111111;
            color: #ffffff;
            font-size: 12px;
            font-weight: 900;
        }

        .canon-label {
            display: inline-block;
            margin-top: 6px;
            padding: 3px 7px;
            border-radius: 999px;
            background: #184b9b;
            color: #ffffff;
            font-size: 12px;
            font-weight: 900;
        }

        @media (max-width: 800px) {
            .hero-title {
                font-size: 32px;
            }

            .day-grid {
                gap: 5px;
            }

            .day {
                min-height: 88px;
                padding: 6px;
            }

            .day-number {
                font-size: 18px;
            }

            .day-line {
                font-size: 12px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_month(df: pd.DataFrame, year: int, month: int) -> str:
    month_df = df[df["Month #"] == month]
    month_name = calendar.month_name[month]
    month_root = digital_root(month)
    yr = year_root(year)

    first_weekday, days_in_month = calendar.monthrange(year, month)

    html = f"""
    <div class="month-box">
        <div class="month-title">{month_name}</div>
        <div class="month-subtitle">Month Root {month_root} · Year Root {yr}</div>

        <div class="day-grid">
            <div class="weekday">Mon</div>
            <div class="weekday">Tue</div>
            <div class="weekday">Wed</div>
            <div class="weekday">Thu</div>
            <div class="weekday">Fri</div>
            <div class="weekday">Sat</div>
            <div class="weekday">Sun</div>
    """

    for _ in range(first_weekday):
        html += '<div class="blank"></div>'

    for day in range(1, days_in_month + 1):
        row = month_df[month_df["Day"] == day].iloc[0]

        date_root = row["Date Root"]
        day_root = row["Day Root"]
        pair = row["Octave Pair"]
        is_gate = row["1-Gate"]
        is_canon = pair in CANON_PAIRS

        classes = "day"
        if is_gate:
            classes += " gate"
        if is_canon:
            classes += " canon"

        html += f"""
        <div class="{classes}">
            <div class="day-number">{day}</div>
            <div class="day-line">Date Root: {date_root}</div>
            <div class="day-line">Day Root: {day_root}</div>
            <div class="day-line">Pair: {pair}</div>
        """

        if is_gate:
            html += '<div class="gate-label">1-GATE</div>'

        if is_canon:
            html += f'<div class="canon-label">{CANON_PAIRS[pair]}</div>'

        html += "</div>"

    html += """
        </div>
    </div>
    """

    return html


st.set_page_config(
    page_title="Breathing Calendar",
    page_icon="🪶",
    layout="wide",
)

inject_css()

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Breathing Calendar</div>
        <div class="hero-subtitle">
            A living calendar-root calculator for date roots, octave pairs,
            1-gates, and mirror-phase grammar.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
canon = df[df["Octave Pair"].isin(CANON_PAIRS.keys())]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Year Root", yr)
col2.metric("Days", len(df))
col3.metric("1-Gates", len(gates))
col4.metric("Canon Pair Days", len(canon))

st.markdown(
    f"""
    <div class="formula">
    Date Root = digital_root(Year Root + Month Root + Day Root)<br>
    For {selected_year}: Date Root = digital_root({yr} + Month Root + Day Root)
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    **Year = field. Month = octave. Day = pulse. Root = phase. Gate = return to One.**
    """
)

if display_mode == "Full Calendar":
    for month in months:
        st.markdown(render_month(df, selected_year, month), unsafe_allow_html=True)

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
