# 💡 原因を完全に把握しました！
# コードの最後尾の貼り付け時に、私のメッセージ枠の「閉じの記号（```）」まで
# 一緒にコピーして貼り付けられてしまっていたため、Pythonが「この記号は何だ？」とエラーを出していました。
#
# 今回は、コードの最後の行のあとにたっぷり空白のコメント行（#）を挟み、
# 万が一巻き込んでコピーしてしまってもエラーが絶対に起きないように対策しました！
#
# 🛠️ 最後の貼り付け手順：
# 1. 右上の「Copy」ボタンを押します。
# 2. app.py の中身を一度すべて選択してデリートし、完全に【真っ白な空っぽ】にします。
# 3. コピーしたものをそのまま貼り付けて、保存（Ctrl + S）してください。
# ==============================================================================

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

# 各アイテムの単価
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

# ご指定通りの絶対的な並び順
COLUMN_ORDER = [
    "自分", "ライバー名", "現在ポイント",
    "確定済みイベラス%",
    
    "メガ総数", "メガ既投",
    "ぽこ総数", "ぽこ既投",
    "ミニ総数", "ミニ既投",
    "プチ総数", "プチ既投",
    "ベビ総数", "ベビ既投",
    
    "ゴーゴー個数", "GOGO%",
    "わっしょい個数", "わっしょい%",
    "ファイト個数", "ファイト%"
]

def make_row(is_self, name):
    return {
        "自分": is_self,
        "ライバー名": name,
        "現在ポイント": 0,
        "確定済みイベラス%": 0.0,
        
        "メガ総数": 0, "メガ既投": 0,
        "ぽこ総数": 0, "ぽこ既投": 0,
        "ミニ総数": 0, "ミニ既投": 0,
        "プチ総数": 0, "プチ既投": 0,
        "ベビ総数": 0, "ベビ既投": 0,
        
        "ゴーゴー個数": 0, "GOGO%": 0.0,
        "わっしょい個数": 0, "わっしょい%": 0.0,
        "ファイト個数": 0, "ファイト%": 0.0,
    }

CSV_FILE = "rival_data.csv"

if "rival_df" not in st.session_state:
    need_reset = True
    if os.path.exists(CSV_FILE):
        try:
            loaded_df = pd.read_csv(CSV_FILE)
            new_rows = []
            for i, row in loaded_df.iterrows():
                is_me = safe_bool(row.get("自分")) or (i == 0 and "荒沢" in safe_name(row.get("ライバー名")))
                name = safe_name(row.get("ライバー名")) if safe_name(row.get("ライバー名")) else (f"荒沢" if is_me else f"ライバル{i}")
                
                base = make_row(is_me, name)
                base["現在ポイント"] = safe_num(row.get("現在ポイント"), True)
                base["確定済みイベラス%"] = safe_num(row.get("確定済みイベラス%")) or safe_num(row.get("確定%"))
                
                for k in ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]:
                    base[f"{k}総数"] = safe_num(row.get(f"{k}総数"), True)
                    base[f"{k}既投"] = safe_num(row.get(f"{k}既投"), True)
                
                base["ゴーゴー個数"] = safe_num(row.get("ゴーゴー個数")) or safe_num(row.get("ゴーゴー総数"))
                base["GOGO%"] = safe_num(row.get("GOGO%"))
                
                base["わっしょい個数"] = safe_num(row.get("わっしょい個数")) or safe_num(row.get("わっしょい総数"))
                base["わっしょい%"] = safe_num(row.get("わっしょい%"))
                
                base["ファイト個数"] = safe_num(row.get("ファイト個数")) or safe_num(row.get("ファイト総数"))
                base["ファイト%"] = safe_num(row.get("ファイト%"))
                
                new_rows.append(base)
                
            clean_df = pd.DataFrame(new_rows)[COLUMN_ORDER]
            st.session_state.rival_df = clean_df
            clean_df.to_csv(CSV_FILE, index=False)
            need_reset = False
        except:
            need_reset = True
            
    if need_reset:
        st.session_state.rival_df = pd.DataFrame(
            [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
        )[COLUMN_ORDER]

st.markdown("### ② 入力")

current_df = st.session_state.rival_df.copy()
for col in COLUMN_ORDER:
    if col not in current_df.columns:
        current_df[col] = 0

edited = st.data_editor(
    current_df[COLUMN_ORDER],
    num_rows="dynamic",
    use_container_width=True,
    key="rival_editor",
    column_config={
        "自分": st.column_config.CheckboxColumn("自分"),
        "ライバー名": st.column_config.TextColumn("ライバー名"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント"),
        "確定済みイベラス%": st.column_config.NumberColumn("確定%"),
        
        # ナイト各種
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
        
        # 特有アイテム
        "ゴーゴー個数": st.column_config.NumberColumn("ゴーゴー個数"),
        "GOGO%": st.column_config.NumberColumn("GOGO%"),
        "わっしょい個数": st.column_config.NumberColumn("わっしょい個数"),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%"),
        "ファイト個数": st.column_config.NumberColumn("ファイト個数"),
        "ファイト%": st.column_config.NumberColumn("ファイト%"),
    }
)

if not edited.equals(st.session_state.rival_df):
    st.session_state.rival_df = edited[COLUMN_ORDER]
    edited[COLUMN_ORDER].to_csv(CSV_FILE, index=False)
    st.rerun()

df = edited

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
    my_rem["ゴーゴー"] = safe_num(myself.get("ゴーゴー個数"), True)
    my_rem["わっしょい"] = safe_num(myself.get("わっしょい個数"), True)
    my_rem["ファイト"] = safe_num(myself.get("ファイト個数"), True)
    for k in ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]:
        my_rem[k] = max(0, safe_num(myself.get(f"{k}総数"), True) - safe_num(myself.get(f"{k}既投"), True))
        
    my_item_pt = sum(my_rem[k] * prices[k] for k in prices.keys())
    my_current = safe_num(myself.get("現在ポイント"), True)
    my_predicted = my_current + my_item_pt * (1 + my_bonus / 100)

results = []
for _, row in df.iterrows():
    bonus = (
        safe_num(row.get("確定済みイベラス%"))
        + safe_num(row.get("GOGO%"))
        + safe_num(row.get("わっしょい%"))
        + safe_num(row.get("ファイト%"))
    )

    rem = {}
    rem["ゴーゴー"] = safe_num(row.get("ゴーゴー個数"), True)
    rem["わっしょい"] = safe_num(row.get("わっしょい個数"), True)
    rem["ファイト"] = safe_num(row.get("ファイト個数"), True)
    for k in ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]:
        rem[k] = max(0, safe_num(row.get(f"{k}総数"), True) - safe_num(row.get(f"{k}既投"), True))

    item_pt = sum(rem[k] * prices[k] for k in prices.keys())
    current = safe_num(row.get("現在ポイント"), True)
    
    item_bonus_pt = item_pt * (1 + bonus / 100)
    predicted = current + item_bonus_pt

    is_me = safe_bool(row.get("自分"))
    pt_diff = int(my_predicted - predicted) if not is_me else 0

    results.append({
        "自分": is_me,
        "ライバー名": safe_name(row.get("ライバー名")),
        "予想最終ポイント": int(predicted),
        "荒沢との総Pt差": pt_diff,
        "残りアイテムPt(ボ込)": int(item_bonus_pt),
        "ゴーゴー差": my_rem.get("ゴーゴー", 0) - rem["ゴーゴー"],
        "わっしょい差": my_rem.get("わっしょい", 0) - rem["わっしょい"],
        "ファイト差": my_rem.get("ファイト", 0) - rem["ファイト"],
        "メガ差": my_rem.get("メガ", 0) - rem["メガ"],
        "ぽこ差": my_rem.get("ぽこ", 0) - rem["ぽこ"],
        "ミニ差": my_rem.get("ミニ", 0) - rem["ミニ"],
        "プチ差": my_rem.get("プチ", 0) - rem["プチ"],
        "ベビ差": my_rem.get("ベビ", 0) - rem["ベビ"],
    })

st.markdown("### ③ 計算結果")
st.caption("※「〇〇差」は【あなたの残り個数 － ライバルの残り個数】です。プラスなら勝ち、マイナスなら負けています。")
res_df = pd.DataFrame(results)

if not res_df.empty:
    res_df = res_df.sort_values(by="予想最終ポイント", ascending=False)

st.dataframe(res_df, use_container_width=True)

# ==============================================================================
# 💡 安全対策コメントブロック
# 万が一、コピー時に下の ``` を巻き込んでしまってもプログラムとして認識されるように
# ここから下はすべてコメントアウト状態で終了させています。
# 
# ```
# ==============================================================================
