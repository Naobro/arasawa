import streamlit as st
import pandas as pd
import unicodedata
import os

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園｜荒沢 予想最終ポイント計算ツール")

# ========== 安全な数値変換 ==========
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
    except Exception:
        return 0

def safe_name(val):
    return "" if val is None else str(val)

def safe_bool(val):
    return bool(val) if val is not None else False

# ========== 単価設定（★ベビを333→555に修正） ==========
if "prices" not in st.session_state:
    st.session_state.prices = {
        "ゴーゴー": 0,
        "わっしょい": 0,
        "ファイト": 111,
        "メガ": 55555,
        "ぽこ": 11111,
        "ミニ": 3333,
        "プチ": 1111,
        "ベビ": 555,   # ★ 333 → 555 に修正
    }
prices = st.session_state.prices

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
    "ファイト個数", "ファイト%",
]
PCT_COLS = ["確定済みイベラス%", "GOGO%", "わっしょい%", "ファイト%"]

def make_row(is_self, name):
    return {
        "自分": is_self, "ライバー名": name,
        "現在ポイント": 0, "確定済みイベラス%": 0.0,
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
                name = safe_name(row.get("ライバー名")) or ("荒沢" if is_me else f"ライバル{i}")
                base = make_row(is_me, name)
                base["現在ポイント"] = safe_num(row.get("現在ポイント"), True)
                base["確定済みイベラス%"] = float(safe_num(row.get("確定済みイベラス%")) or safe_num(row.get("確定%")))
                for k in ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]:
                    base[f"{k}総数"] = safe_num(row.get(f"{k}総数"), True)
                    base[f"{k}既投"] = safe_num(row.get(f"{k}既投"), True)
                base["ゴーゴー個数"] = safe_num(row.get("ゴーゴー個数"), True) or safe_num(row.get("ゴーゴー総数"), True)
                base["GOGO%"] = float(safe_num(row.get("GOGO%")))
                base["わっしょい個数"] = safe_num(row.get("わっしょい個数"), True) or safe_num(row.get("わっしょい総数"), True)
                base["わっしょい%"] = float(safe_num(row.get("わっしょい%")))
                base["ファイト個数"] = safe_num(row.get("ファイト個数"), True) or safe_num(row.get("ファイト総数"), True)
                base["ファイト%"] = float(safe_num(row.get("ファイト%")))
                new_rows.append(base)
            clean_df = pd.DataFrame(new_rows)[COLUMN_ORDER]
            # ★パーセント列を確実にfloat型へ強制
            for col in PCT_COLS:
                clean_df[col] = clean_df[col].astype(float)
            st.session_state.rival_df = clean_df
            clean_df.to_csv(CSV_FILE, index=False)
            need_reset = False
        except Exception:
            need_reset = True

    if need_reset:
        init_df = pd.DataFrame(
            [make_row(True, "荒沢")] + [make_row(False, f"ライバル{i}") for i in range(1, 6)]
        )[COLUMN_ORDER]
        for col in PCT_COLS:
            init_df[col] = init_df[col].astype(float)
        st.session_state.rival_df = init_df

# ========== 入力テーブル ==========
st.markdown("### ② 入力")
st.caption(
    "・「自分」は荒沢の行だけチェックしてください。\n"
    "・ナイトは「総数」「既投」を入れると「残り」が自動計算されます。\n"
    "・％欄は小数点で入力できます（例：48.12）。\n"
    "・数値はカンマなしで入力し、入力後は必ずEnterかTabキーで確定してください。"
)

current_df = st.session_state.rival_df.copy()
for col in COLUMN_ORDER:
    if col not in current_df.columns:
        current_df[col] = 0.0 if col in PCT_COLS else 0

edited = st.data_editor(
    current_df[COLUMN_ORDER],
    num_rows="dynamic",
    use_container_width=True,
    key="rival_editor",
    column_config={
        "自分": st.column_config.CheckboxColumn("自分"),
        "ライバー名": st.column_config.TextColumn("ライバー名"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント", format="%d", min_value=0, step=1000),
        # ★％列は小数対応（48.12などが入力できる）
        "確定済みイベラス%": st.column_config.NumberColumn("確定%", format="%.2f", step=0.01, min_value=0.0),
        "GOGO%": st.column_config.NumberColumn("GOGO%", format="%.2f", step=0.01, min_value=0.0),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%", format="%.2f", step=0.01, min_value=0.0),
        "ファイト%": st.column_config.NumberColumn("ファイト%", format="%.2f", step=0.01, min_value=0.0),
        "メガ総数": st.column_config.NumberColumn("メガ総数", format="%d", min_value=0, step=1),
        "メガ既投": st.column_config.NumberColumn("メガ既投", format="%d", min_value=0, step=1),
        "ぽこ総数": st.column_config.NumberColumn("ぽこ総数", format="%d", min_value=0, step=1),
        "ぽこ既投": st.column_config.NumberColumn("ぽこ既投", format="%d", min_value=0, step=1),
        "ミニ総数": st.column_config.NumberColumn("ミニ総数", format="%d", min_value=0, step=1),
        "ミニ既投": st.column_config.NumberColumn("ミニ既投", format="%d", min_value=0, step=1),
        "プチ総数": st.column_config.NumberColumn("プチ総数", format="%d", min_value=0, step=1),
        "プチ既投": st.column_config.NumberColumn("プチ既投", format="%d", min_value=0, step=1),
        "ベビ総数": st.column_config.NumberColumn("ベビ総数", format="%d", min_value=0, step=1),
        "ベビ既投": st.column_config.NumberColumn("ベビ既投", format="%d", min_value=0, step=1),
        "ゴーゴー個数": st.column_config.NumberColumn("ゴーゴー個数", format="%d", min_value=0, step=1),
        "わっしょい個数": st.column_config.NumberColumn("わっしょい個数", format="%d", min_value=0, step=1),
        "ファイト個数": st.column_config.NumberColumn("ファイト個数", format="%d", min_value=0, step=1),
    },
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

my_rem, my_predicted, my_item_bonus_pt, my_bonus, my_current = {}, 0, 0, 0, 0

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
    my_item_bonus_pt = my_item_pt * (1 + my_bonus / 100)
    my_predicted = my_current + my_item_bonus_pt

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
        "現在Pt": current,
        "合計ボーナス%": round(bonus, 2),
        "残りアイテムPt(ボ込)": int(item_bonus_pt),
        "予想最終ポイント": int(predicted),   # ★数値型のまま保持（正しくソートするため）
        "荒沢との総Pt差": pt_diff,
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
st.caption("※「〇〇差」は【荒沢の残り個数－ライバルの残り個数】。プラスなら荒沢有利、マイナスなら不利です。")

res_df = pd.DataFrame(results)
if not res_df.empty:
    # ★数値のままソートしてから表示用に変換する（文字列ソートによる誤順位を防止）
    res_df = res_df.sort_values(by="予想最終ポイント", ascending=False).reset_index(drop=True)
    res_df.index += 1

display_df = res_df.copy()
for col in ["現在Pt", "残りアイテムPt(ボ込)", "予想最終ポイント", "荒沢との総Pt差"]:
    display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}")

st.dataframe(display_df, use_container_width=True)

# ========== 検算用：荒沢の計算内訳 ==========
if myself is not None:
    st.markdown("### ④ 荒沢の計算内訳（検算用）")
    col1, col2, col3 = st.columns(3)
    col1.metric("現在ポイント", f"{my_current:,} pt")
    col2.metric("残りアイテムPt（ボーナス込み）", f"{int(my_item_bonus_pt):,} pt")
    col3.metric("合計ボーナス%", f"{my_bonus:.2f} %")
    st.markdown(
        f"$$\\text{{予想最終ポイント}} = {my_current:,} + {int(my_item_bonus_pt):,} = {int(my_predicted):,}\\text{{ pt}}$$"
    )
