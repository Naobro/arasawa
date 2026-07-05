import streamlit as st
import pandas as pd
import unicodedata
import os

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園｜荒沢 予想最終ポイント計算ツール")

# ========== ① 安全な数値変換 ==========
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
    return "" if (val is None or (isinstance(val, float) and pd.isna(val))) else str(val)

def safe_bool(val):
    return bool(val) if (val is not None and not (isinstance(val, float) and pd.isna(val))) else False


# ========== ② 単価 ==========
st.markdown("### ① ナイト単価")

if "prices" not in st.session_state:
    st.session_state.prices = {"メガ": 55555, "ぽこ": 11111, "ミニ": 3333, "プチ": 1111, "ベビ": 333}

with st.form("price_form"):
    c1, c2, c3, c4, c5 = st.columns(5)

    p_mega = c1.number_input("メガ", value=st.session_state.prices["メガ"])
    p_poko = c2.number_input("ぽこ", value=st.session_state.prices["ぽこ"])
    p_mini = c3.number_input("ミニ", value=st.session_state.prices["ミニ"])
    p_puchi = c4.number_input("プチ", value=st.session_state.prices["プチ"])
    p_baby = c5.number_input("ベビ", value=st.session_state.prices["ベビ"])

    if st.form_submit_button("更新"):
        st.session_state.prices = {
            "メガ": p_mega,
            "ぽこ": p_poko,
            "ミニ": p_mini,
            "プチ": p_puchi,
            "ベビ": p_baby,
        }

prices = st.session_state.prices


# ========== ③ データ ==========
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
        st.session_state.rival_df = pd.read_csv(CSV_FILE)
    else:
        rows = [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
        st.session_state.rival_df = pd.DataFrame(rows)


# ========== ④ 編集テーブル ==========
st.markdown("### ② 入力")

def save_csv():
    df = st.session_state["rival_editor"]
    st.session_state.rival_df = df.copy()
    df.to_csv(CSV_FILE, index=False)

edited = st.data_editor(
    st.session_state.rival_df,
    num_rows="dynamic",
    use_container_width=True,
    key="rival_editor",
    on_change=save_csv,
    column_config={
        "自分": st.column_config.CheckboxColumn("自分"),
        "ライバー名": st.column_config.TextColumn("ライバー名"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント"),
        "確定済みイベラス%": st.column_config.NumberColumn("確定%"),
        "GOGO%": st.column_config.NumberColumn("GOGO%"),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%"),
        "ファイト%": st.column_config.NumberColumn("ファイト%"),
    }
)


# ========== ⑤ 計算 ==========
st.markdown("### ③ 結果")

night_keys = ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]
results = []

for _, row in edited.iterrows():

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
            - safe_num(row.get(f"{k}既投"), True)
        )

    night_pt = sum(rem[k] * prices[k] for k in night_keys)
    current = safe_num(row.get("現在ポイント"), True)
    predicted = current + night_pt * (1 + bonus / 100)

    results.append({
        "ライバー名": safe_name(row.get("ライバー名")),
        "予想": int(predicted),
    })

res_df = pd.DataFrame(results)

st.dataframe(res_df, use_container_width=True)
