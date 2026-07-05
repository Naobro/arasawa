import streamlit as st
import pandas as pd
import unicodedata
import os

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園｜荒沢 予想最終ポイント計算ツール")

def safe_num(val, as_int=False):
    if val is None:
        return 0
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return 0
    s = unicodedata.normalize("NFKC", s)
    s = s.replace(",", "").replace("%", "").replace("％", "")
    try:
        v = float(s)
        if pd.isna(v):
            return 0
        return int(round(v)) if as_int else v
    except:
        return 0

def safe_name(val):
    return "" if val is None else str(val)

def safe_bool(val):
    return bool(val) if val is not None else False

if "prices" not in st.session_state:
    st.session_state.prices = {
        "メガ": 55555, "ぽこ": 11111, "ミニ": 3333, "プチ": 1111, "ベビ": 333
    }

prices = st.session_state.prices

def make_row(is_self, name):
    return {
        "自分": is_self,
        "ライバー名": name,
        "現在ポイント": 0,
        "確定済みイベラス%": 0.0,
        "GOGO%": 0.0,
        "わっしょい%": 0.0,
        "ファイト%": 0.0,
        "メガ総数": 0,
        "メガ既投": 0,
        "ぽこ総数": 0,
        "ぽこ既投": 0,
        "ミニ総数": 0,
        "ミニ既投": 0,
        "プチ総数": 0,
        "プチ既投": 0,
        "ベビ総数": 0,
        "ベビ既投": 0,
    }

CSV_FILE = "rival_data.csv"

if "rival_df" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            st.session_state.rival_df = pd.read_csv(CSV_FILE)
        except:
            st.session_state.rival_df = pd.DataFrame(
                [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
            )
    else:
        st.session_state.rival_df = pd.DataFrame(
            [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
        )

st.markdown("### ② 入力")

edited = st.data_editor(
    st.session_state.rival_df,
    num_rows="dynamic",
    use_container_width=True,
    key="rival_editor",
    column_config={
        "自分": st.column_config.CheckboxColumn("自分"),
        "ライバー名": st.column_config.TextColumn("ライバー名"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント"),
        "確定済みイベラス%": st.column_config.NumberColumn("確定%"),
        "GOGO%": st.column_config.NumberColumn("GOGO%"),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%"),
        "ファイト%": st.column_config.NumberColumn("ファイト%"),
        "メガ総数": st.column_config.NumberColumn("メガ総数"),
        "メガ既投": st.column_config.NumberColumn("メガ既投"),
        "ぽこ総数": st.column_config.NumberColumn("ぽこ総数"),
        "ぽこ既投": st.column_config.NumberColumn("ぽこ既投"),
        "ミニ総数": st.column_config.NumberColumn("ミニ総数"),
        "ミニ既投": st.column_config.NumberColumn("ミニ既投"),
        "プチ総数": st.column_config.NumberColumn("プチ総数"),
        "プチ既投": st.column_config.NumberColumn("プチ既投"),
        "ベビ総数": st.column_config.NumberColumn("ベビ総数"),
        "ベビ既投": st.column_config.NumberColumn("ベビ既投"),
    }
)

if not edited.equals(st.session_state.rival_df):
    st.session_state.rival_df = edited
    edited.to_csv(CSV_FILE, index=False)
    st.rerun()

df = edited

night_keys = ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]
results = []

for _, row in df.iterrows():
    bonus = (
        safe_num(row.get("確定済みイベラス%"))
        + safe_num(row.get("GOGO%"))
        + safe_num(row.get("わっしょい%"))
        + safe_num(row.get("ファイト%"))
    )

    rem = {}
    for k in night_keys:
        rem[k] = max(
            0,
            safe_num(row.get(f"{k}総数"), True)
            - safe_num(row.get(f"{k}既投"), True),
        )

    night_pt = sum(rem[k] * prices[k] for k in night_keys)
    current = safe_num(row.get("現在ポイント"), True)
    predicted = current + night_pt * (1 + bonus / 100)

    results.append({
        "自分": safe_bool(row.get("自分")),
        "ライバー名": safe_name(row.get("ライバー名")),
        "予想最終ポイント": int(predicted),
    })

st.markdown("### ③ 計算結果")
res_df = pd.DataFrame(results)

if not res_df.empty:
    res_df = res_df.sort_values(by="予想最終ポイント", ascending=False)

st.dataframe(res_df, use_container_width=True)
