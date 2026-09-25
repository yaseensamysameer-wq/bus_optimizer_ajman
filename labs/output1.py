"""
This is the file the web page pulls from.
Replace the example code below with your own code.
Each function just needs to RETURN something for app.py to display.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Text placeholders ----------
PAGE_TITLE = "Bus Optimizer Ajman"
SUBTITLE = "Turning Ajman transportation schedules into an intelligent system"
SIDEBAR_TEXT = "This project is built 100% by human"
FOOTER_TEXT = ""


# ---------- Key numbers: return a list of (label, value, change) ----------
def get_metrics():
    return [
        ("Metric 1", "1,234", "+5%"),
        ("Metric 2", "56.7", "-2%"),
        ("Metric 3", "89", "+12"),
        ("Metric 4", "4.2k", "+0.3k"),
    ]


# ---------- Text: return a string (markdown works) ----------
def get_text():
    return "Replace this with your own **summary text**, results, or notes."


# ---------- Charts: return a matplotlib figure ----------
def get_chart_1():
    x = np.arange(1, 13)
    y = np.random.randint(10, 100, size=12)
    fig, ax = plt.subplots()
    ax.plot(x, y, color="#0F8B8D", linewidth=2.5)
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def get_chart_2():
    labels = ["A", "B", "C", "D"]
    values = np.random.randint(10, 100, size=4)
    fig, ax = plt.subplots()
    ax.bar(labels, values, color="#14213D")
    ax.spines[["top", "right"]].set_visible(False)
    return fig


# ---------- Table: return a pandas DataFrame ----------
def get_table():
    return pd.DataFrame(
        {
            "Name": ["Item 1", "Item 2", "Item 3"],
            "Value": [10, 20, 30],
            "Status": ["Done", "In progress", "Planned"],
        }
    )


# ---------- Anything else: text, a DataFrame, a figure, etc. ----------
def get_extra():
    return "Put anything else here."