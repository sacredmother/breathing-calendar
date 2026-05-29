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
#
# Shows:
# - Date Root
# - Day Root
# - Root Pair = Month Root / Day Root
# - Canon Octave Pair, when applicable
# - Additive Operator
# - Carrier Operator
# - Limited Mirror Operator
# - 1-Gates
# - 40 / 40 resonance for 2026
# ============================================================


# ---------- Core math ----------

def digital_root(n: int) -> int:
    """Return the 1-9 digital root."""
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)


def digit_sum(n: int) -> int:
    """Return sum of digits."""
    return sum(int(d) for d in str(abs(n)))


def year_root(year: int) -> int:
    """Return digital root of a year."""
    return digital_root(digit_sum(year))


def root_reduce_expression(value: int) -> str:
    """
    Show root reduction clearly.
    Example:
    7  -> 7
    10 -> 10 → 1
    11 -> 11 → 2
    """
    root = digital_root(value)
    if value == root:
        return str(root)
    return f"{value} → {root}"


# ---------- Canon octave pairs ----------

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


# ---------- Operators ----------

def additive_operator(month_root: int, day_root: int, yr_root: int) -> str:
    """
    Main outward construction:
    Month Root + Day Root + Year Root = Date Root
    """
    raw_sum = month_root + day_root + yr_root
    return f"{month_root} + {day_root} + {yr_root} = {root_reduce_expression(raw_sum)}"


def carrier_operator(month_root: int, yr_root: int, day_root: int) -> str:
    """
    Month Root + Year Root creates a fixed month/year carrier.
    Day Root moves through this carrier.

    Example:
    May 2026:
    Month Root 5 + Year Root 1 = carrier 6
    Day Root 4 + carrier 6 = 10 → 1
    """
    carrier = month_root + yr_root
    raw_sum = day_root + carrier
    return f"{day_root} + {carrier} = {root_reduce_expression(raw_sum)}"


def visible_day_digit(day: int) -> int:
    """
    The visible day digit used in the user's mirror path.

    Examples:
    5  -> 5
    13 -> 3
    20 -> 10
    21 -> 1
    29 -> 9
    30 -> 10
    31 -> 1

    Zero is treated as 10 because it is a completion / threshold digit.
    """
    ones = day % 10
    if ones == 0:
        return 10
    return ones


def direct_path_to_date_root(base: int, date_root: int) -> str:
    """
    Create the cleanest direct operator from a given base to the date root.

    Examples:
    5 to 7  -> 5 + 2 = 7
    9 to 7  -> 9 - 2 = 7
    10 to 8 -> 10 - 2 = 8
    3 to 1  -> 3 - 2 = 1
    """
    if base == date_root:
        return f"{base} = {date_root}"

    if base < date_root:
        diff = date_root - base
        return f"{base} + {diff} = {date_root}"

    diff = base - date_root
    return f"{base} - {diff} = {date_root}"


def mirror_operator(day: int, day_root: int, date_root: int) -> str:
    """
    Limited mirror grammar based on the user's method.

    It shows only:
    1. Visible digit path
    2. Day-root path

    This prevents the app from generating too many unrelated candidates.

    Example:
    April 29, 2026:
    date root 7
    visible digit 9 -> 9 - 2 = 7
    day root 2      -> 2 + 5 = 7

    Output:
    9 - 2 = 7 | 2 + 5 = 7
    """
    digit_base = visible_day_digit(day)

    digit_path = direct_path_to_date_root(digit_base, date_root)
    root_path = direct_path_to_date_root(day_root, date_root)

    if digit_path == root_path:
        return digit_path

    return f"{digit_path} | {root_path}"


def gate_family(date_root: int, is_gate: bool, is_canon: bool) -> str:
    """Classify the date's main pattern family."""
    families = []

    if is_gate:
        families.append("1-Gate")

    if is_canon:
        families.append("Canon Pair")

    if not families:
        families.append(f"Phase {date_root}")

    return " + ".join(families)


# ---------- Build calendar table ----------

def build_year_table(year: int) -> pd.DataFrame:
    """Build one row for every date in the selected year."""
    yr = year_root(year)
    rows = []

    for month in range(1, 13):
        month_root = digital_root(month)
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]
        month_year_carrier = month_root + yr

        for day in range(1, days_in_month + 1):
            day_root = digital_root(day)
            raw_sum = month_root + day_root + yr
            date_root = digital_root(raw_sum)
            root_pair = f"{month_root}/{day_root}"

            is_gate = date_root == 1
            is_canon = root_pair in CANON_PAIRS

            add_op = additive_operator(month_root, day_root, yr)
            carrier_op = carrier_operator(month_root, yr, day_root)
            mirror_op = mirror_operator(day, day_root, date_root)

            rows.append(
                {
                    "Date": date(year, month, day),
                    "Month": month_name,
                    "Month #": month,
                    "Day": day,
                    "Year Root": yr,
                    "Month Root": month_root,
                    "Day Root": day_root,
                    "Visible Digit": visible_day_digit(day),
                    "Month/Year Carrier": month_year_carrier,
                    "Raw Sum": raw_sum,
                    "Date Root": date_root,
                    "Root Pair": root_pair,
                    "1-Gate": is_gate,
                    "Canon Pair": is_canon,
                    "Canon Meaning": CANON_PAIRS.get(root_pair, ""),
                    "Additive Operator": add_op,
                    "Carrier Operator": carrier_op,
                    "Mirror Operator": mirror_op,
                    "Gate Family": gate_family(date_root, is_gate, is_canon),
                }
            )

    return pd.DataFrame(rows)


# ---------- Render calendar ----------

def render_day(row: pd.Series) -> None:
    """Render one day with native Streamlit components only."""
    with st.container(border=True):
        st.markdown(f"### {row['Day']}")

        st.write(f"**Date Root:** {row['Date Root']}")
        st.write(f"**Day Root:** {row['Day Root']}")
        st.write(f"**Root Pair:** {row['Root Pair']}")

        if row["Canon Pair"]:
            st.info(f"Canon Pair: {row['Canon Meaning']}")

        if row["1-Gate"]:
            st.warning("GATE: Date Root returns to 1")

        st.caption(f"Add: {row['Additive Operator']}")
        st.caption(f"Carrier: {row['Carrier Operator']}")
        st.caption(f"Mirror: {row['Mirror Operator']}")

        with st.expander("More", expanded=False):
            st.write(f"**Visible Digit:** {row['Visible Digit']}")
            st.write(f"**Month/Year Carrier:** {row['Month/Year Carrier']}")
            st.write(f"**Gate Family:** {row['Gate Family']}")


def render_month(df: pd.DataFrame, year: int, month: int) -> None:
    """Render one month as a seven-column calendar."""
    month_name = calendar.month_name[month]
    month_root = digital_root(month)
    yr = year_root(year)
    carrier = month_root + yr

    st.divider()
    st.header(month_name)
    st.caption(
        f"Month Root {month_root} · Year Root {yr} · Month/Year Carrier {carrier}"
    )

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
            cols[i].empty()
        else:
            row = month_df[month_df["Day"] == current_day].iloc[0]
            with cols[i]:
                render_day(row)
            current_day += 1

    # Remaining weeks
    while current_day <= days_in_month:
        cols = st.columns(7)
        for i in range(7):
            if current_day <= days_in_month:
                row = month_df[month_df["Day"] == current_day].iloc[0]
                with cols[i]:
                    render_day(row)
                current_day += 1
            else:
                cols[i].empty()


# ---------- Summary tables ----------

def gate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize 1-gates by month."""
    gates = df[df["1-Gate"]].copy()

    if gates.empty:
        return pd.DataFrame()

    return (
        gates.groupby(["Month #", "Month", "Month Root"])
        .agg(
            Gate_Days=("Day", lambda x: ", ".join(str(v) for v in x)),
            Gate_Day_Roots=("Day Root", lambda x: ", ".join(str(v) for v in sorted(set(x)))),
            Root_Pairs=("Root Pair", lambda x: ", ".join(x)),
            Canon_Meanings=("Canon Meaning", lambda x: ", ".join(v for v in x if v)),
            Gate_Count=("Day", "count"),
        )
        .reset_index()
        .sort_values("Month #")
    )


def pair_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize root pairs."""
    return (
        df.groupby(["Root Pair", "Month Root", "Day Root"])
        .agg(
            Count=("Date", "count"),
            Gate_Count=("1-Gate", "sum"),
            Canon_Pair=("Canon Pair", "max"),
            Canon_Meaning=("Canon Meaning", lambda x: next((v for v in x if v), "")),
            First_Date=("Date", "min"),
            Last_Date=("Date", "max"),
        )
        .reset_index()
        .sort_values(["Month Root", "Day Root"])
    )


def operator_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize pattern families."""
    return (
        df.groupby(["Date Root", "Gate Family"])
        .agg(
            Count=("Date", "count"),
            First_Date=("Date", "min"),
            Last_Date=("Date", "max"),
        )
        .reset_index()
        .sort_values(["Date Root", "Gate Family"])
    )


def resonance_statement(year: int, gate_count: int, canon_count: int) -> str:
    """Return a special statement when gates and canon pairs match."""
    if gate_count == canon_count:
        return (
            f"{year} shows a {gate_count} / {canon_count} resonance: "
            f"{gate_count} 1-Gates and {canon_count} Canon Pair days."
        )

    return (
        f"{year} shows {gate_count} 1-Gates and {canon_count} Canon Pair days."
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
A living calendar-root calculator for date roots, root pairs, canon octave pairings,
1-gates, additive operators, carrier operators, and limited mirror paths.

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
            "Operator Summary",
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

gate_count = len(gates)
canon_count = len(canon)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Year Root", yr)
col2.metric("Days", len(df))
col3.metric("1-Gates", gate_count)
col4.metric("Canon Pair Days", canon_count)

if gate_count == canon_count:
    st.success(resonance_statement(selected_year, gate_count, canon_count))
else:
    st.info(resonance_statement(selected_year, gate_count, canon_count))

st.info(
    f"Date Root = digital_root(Year Root + Month Root + Day Root). "
    f"For {selected_year}: Date Root = digital_root({yr} + Month Root + Day Root)."
)

st.markdown(
    """
### Reading the Calendar

- **Date Root** = visible phase of the date
- **Day Root** = root of the day number
- **Root Pair** = Month Root / Day Root
- **Canon Pair** = one of the tracked octave-pair relationships
- **Additive Operator** = Month Root + Day Root + Year Root
- **Carrier Operator** = Day Root + fixed Month/Year carrier
- **Mirror Operator** = limited mirror path from visible day digit and day-root
- **GATE** = Date Root returns to 1
"""
)

if selected_year == 2026:
    st.success(
        "2026 has Year Root 1. The year supplies the One Light carrier. "
        "The date-field reveals a 40 / 40 resonance: forty 1-Gates and forty Canon Pair days."
    )

# ---------- Display modes ----------

if display_mode == "Full Calendar":
    for month in months:
        render_month(df, selected_year, month)

elif display_mode == "Only 1-Gates":
    st.header("1-Gates")

    gate_cols = [
        "Date",
        "Month",
        "Day",
        "Year Root",
        "Month Root",
        "Day Root",
        "Visible Digit",
        "Month/Year Carrier",
        "Date Root",
        "Root Pair",
        "Canon Pair",
        "Canon Meaning",
        "Additive Operator",
        "Carrier Operator",
        "Mirror Operator",
        "Gate Family",
    ]

    st.dataframe(
        gates[gate_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("1-Gates by Month")
    st.dataframe(
        gate_summary(df),
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Only Canon Pairs":
    st.header("Canon Octave Pair Days")

    canon_cols = [
        "Date",
        "Month",
        "Day",
        "Year Root",
        "Month Root",
        "Day Root",
        "Visible Digit",
        "Date Root",
        "Root Pair",
        "1-Gate",
        "Canon Meaning",
        "Additive Operator",
        "Carrier Operator",
        "Mirror Operator",
        "Gate Family",
    ]

    st.dataframe(
        canon[canon_cols],
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Table View":
    st.header("Full Table")

    full_cols = [
        "Date",
        "Month",
        "Day",
        "Year Root",
        "Month Root",
        "Day Root",
        "Visible Digit",
        "Month/Year Carrier",
        "Raw Sum",
        "Date Root",
        "Root Pair",
        "1-Gate",
        "Canon Pair",
        "Canon Meaning",
        "Additive Operator",
        "Carrier Operator",
        "Mirror Operator",
        "Gate Family",
    ]

    st.dataframe(
        df[full_cols],
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Pair Summary":
    st.header("Root Pair Summary")

    st.dataframe(
        pair_summary(df),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Canon Pair Key")

    key_df = pd.DataFrame(
        [{"Root Pair": pair, "Canon Meaning": meaning} for pair, meaning in CANON_PAIRS.items()]
    )

    st.dataframe(
        key_df,
        use_container_width=True,
        hide_index=True,
    )

elif display_mode == "Operator Summary":
    st.header("Operator Summary")

    st.dataframe(
        operator_summary(df),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("All Operators")

    operator_cols = [
        "Date",
        "Month",
        "Day",
        "Date Root",
        "Root Pair",
        "Visible Digit",
        "Additive Operator",
        "Carrier Operator",
        "Mirror Operator",
        "Gate Family",
    ]

    st.dataframe(
        df[operator_cols],
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
