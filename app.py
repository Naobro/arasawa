

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
        "ゴーゴー": 0,      
        "わっしょい": 0,    
        "ファイト": 111,    
        "メガ": 55555, 
        "ぽこ": 11111, 
        "ミニ": 3333, 
        "プチ": 1111, 
        "ベビ": 333
    }

prices = st.session_state.prices

# 表示させたい絶対的な列の順番を定義
COLUMN_ORDER = [
    "自分", "ライバー名", "現在ポイント",
    "ゴーゴー総数", "ゴーゴー既投", "GOGO%",
    "わっしょい総数", "わっしょい既投", "わっしょい%",
    "ファイト総数", "ファイト既投", "ファイト%",
    "メガ総数", "メガ既投",
    "ぽこ総数", "ぽこ既投",
    "ミニ総数", "ミニ既投",
    "プチ総数", "プチ既投",
    "ベビ総数", "ベビ既投",
    "確定済みイベラス%"
]

def make_row(is_self, name):
    return {
        "自分": is_self,
        "ライバー名": name,
        "現在ポイント": 0,
        "ゴーゴー総数": 0, "ゴーゴー既投": 0, "GOGO%": 0.0,
        "わっしょい総数": 0, "わっしょい既投": 0, "わっしょい%": 0.0,
        "ファイト総数": 0, "ファイト既投": 0, "ファイト%": 0.0,
        "メガ総数": 0, "メガ既投": 0,
        "ぽこ総数": 0, "ぽこ既投": 0,
        "ミニ総数": 0, "ミニ既投": 0,
        "プチ総数": 0, "プチ既投": 0,
        "ベビ総数": 0, "ベビ既投": 0,
        "確定済みイベラス%": 0.0,
    }

CSV_FILE = "rival_data.csv"

if "rival_df" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            loaded_df = pd.read_csv(CSV_FILE)
            base_row = make_row(True, "dummy")
            # 足りない列があれば補完
            for col in base_row.keys():
                if col not in loaded_df.columns:
                    loaded_df[col] = base_row[col]
            # ➔ ➔ ➔ 【最重要】ここで強制的に「個数 ➔ ポイント」の順番に並び替える ➔ ➔ ➔
            loaded_df = loaded_df[COLUMN_ORDER]
            st.session_state.rival_df = loaded_df
        except:
            st.session_state.rival_df = pd.DataFrame(
                [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
            )[COLUMN_ORDER]
    else:
        st.session_state.rival_df = pd.DataFrame(
            [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
        )[COLUMN_ORDER]

st.markdown("### ② 入力")

# 画面表示用の設定。並び順が固定されるようにCOLUMN_ORDERに沿って適用
edited = st.data_editor(
    st.session_state.rival_df[COLUMN_ORDER],  # 常に正しい列順でエディタに渡す
    num_rows="dynamic",
    use_container_width=True,
    key="rival_editor",
    column_config={
        "自分": st.column_config.CheckboxColumn("自分"),
        "ライバー名": st.column_config.TextColumn("ライバー名"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント"),
        
        # ゴーゴー
        "ゴーゴー総数": st.column_config.NumberColumn("ゴーゴー総数"),
        "ゴーゴー既投": st.column_config.NumberColumn("ゴーゴー既投"),
        "GOGO%": st.column_config.NumberColumn("GOGO%"),
        
        # わっしょい
        "わっしょい総数": st.column_config.NumberColumn("わっしょい総数"),
        "わっしょい既投": st.column_config.NumberColumn("わっしょい既投"),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%"),
        
        # ファイト
        "ファイト総数": st.column_config.NumberColumn("ファイト総数"),
        "ファイト既投": st.column_config.NumberColumn("ファイト既投"),
        "ファイト%": st.column_config.NumberColumn("ファイト%"),
        
        # ナイト
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
        
        "確定済みイベラス%": st.column_config.NumberColumn("確定%"),
    }
)

if not edited.equals(st.session_state.rival_df):
    st.session_state.rival_df = edited[COLUMN_ORDER]
    edited[COLUMN_ORDER].to_csv(CSV_FILE, index=False)
    st.rerun()

df = edited
night_keys = ["ゴーゴー", "わっしょい", "ファイト", "メガ", "ぽこ", "ミニ", "プチ", "ベビ"]

myself = None
for _, row in df.iterrows():
    if safe_bool(row.get("自分")):
        myself = row
        break
if myself is None and len(df) > 0:
    myself = df.iloc[0]

my_rem = {}
my_predicted = 0
if myself is not None:
    my_bonus = (
        safe_num(myself.get("確定済みイベラス%"))
        + safe_num(myself.get("GOGO%"))
        + safe_num(myself.get("わっしょい%"))
        + safe_num(myself.get("ファイト%"))
    )
    for k in night_keys:
        my_rem[k] = max(0, safe_num(myself.get(f"{k}総数"), True) - safe_num(myself.get(f"{k}既投"), True))
    my_night_pt = sum(my_rem[k] * prices[k] for k in night_keys)
    my_current = safe_num(myself.get("現在ポイント"), True)
    my_predicted = my_current + my_night_pt * (1 + my_bonus / 100)

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
        rem[k] = max(0, safe_num(row.get(f"{k}総数"), True) - safe_num(row.get(f"{k}既投"), True))

    night_pt = sum(rem[k] * prices[k] for k in night_keys)
    current = safe_num(row.get("現在ポイント"), True)
    
    item_bonus_pt = night_pt * (1 + bonus / 100)
    predicted = current + item_bonus_pt

    is_me = safe_bool(row.get("自分"))
    pt_diff = int(my_predicted - predicted) if not is_me else 0

    results.append({
        "自分": is_me,
        "ライバー名": safe_name(row.get("ライバー名")),
        "予想最終ポイント": int(predicted),
        "荒沢との総Pt差": pt_diff,
        "残りアイテムPt(ボ込)": int(item_bonus_pt),
        "メガ差": my_rem.get("メガ", 0) - rem["メガ"],
        "ぽこ差": my_rem.get("ぽこ", 0) - rem["ぽこ"],
        "ミニ差": my_rem.get("ミニ", 0) - rem["ミニ"],
        "プチ差": my_rem.get("プチ", 0) - rem["プチ"],
        "ベビ差": my_rem.get("ベビ", 0) - rem["ベビ"],
        "ファイト差": my_rem.get("ファイト", 0) - rem["ファイト"],
    })

st.markdown("### ③ 計算結果")
st.caption("※「〇〇差」は【あなたの残り個数 － ライバルの残り個数】です。プラスなら勝ち、マイナスなら負けています。")
res_df = pd.DataFrame(results)

if not res_df.empty:
    res_df = res_df.sort_values(by="予想最終ポイント", ascending=False)

st.dataframe(res_df, use_container_width=True)
