import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園｜荒沢 予想最終ポイント計算ツール")

# ========== ① ナイト単価設定 ==========
st.markdown("### ① ナイト1個あたりのポイント単価")
st.warning(
    "⚠️ 以下は仮の初期値です。実際の枠でナイトをタップした際に表示される"
    "「このアイテムで◯pt応援」の数値に必ず書き換えてください。"
)

c1, c2, c3, c4, c5 = st.columns(5)
pt_mega  = c1.number_input("メガナイト単価",  value=55555, step=100)
pt_poko  = c2.number_input("ぽこナイト単価",  value=11111, step=100)
pt_mini  = c3.number_input("ミニナイト単価",  value=3333,  step=100)
pt_puchi = c4.number_input("プチナイト単価",  value=1111,  step=100)
pt_baby  = c5.number_input("ベビナイト単価",  value=333,   step=100)

prices = {"メガ": pt_mega, "ぽこ": pt_poko, "ミニ": pt_mini, "プチ": pt_puchi, "ベビ": pt_baby}

# ========== ② デフォルトデータ（荒沢＋ライバル5人） ==========
def make_row(is_self, name):
    return {
        "自分": is_self, "ライバー名": name,
        "現在ポイント": 0, "確定済みイベラス%": 0.0,
        "GOGO個数": 0, "GOGO%": 0.0,
        "わっしょい個数": 0, "わっしょい%": 0.0,
        "ファイト個数": 0, "ファイト%": 0.0,
        "メガ総数": 0, "メガ既投": 0,
        "ぽこ総数": 0, "ぽこ既投": 0,
        "ミニ総数": 0, "ミニ既投": 0,
        "プチ総数": 0, "プチ既投": 0,
        "ベビ総数": 0, "ベビ既投": 0,
    }

if "df" not in st.session_state:
    _rows = [make_row(True, "荒沢")]
    for i in range(1, 6):
        _rows.append(make_row(False, f"ライバル{i}"))
    st.session_state.df = pd.DataFrame(_rows)

# ========== ③ 安全な数値変換（TypeError対策の本体） ==========
def safe_num(val, as_int=False):
    """None / NaN / 空文字 / 不正な文字列などを安全に 0 として扱う"""
    try:
        v = float(val)
        if pd.isna(v):
            return 0
        return int(v) if as_int else v
    except (TypeError, ValueError):
        return 0

def safe_name(val):
    return "" if pd.isna(val) else str(val)

def safe_bool(val):
    return bool(val) if pd.notna(val) else False

# ========== ④ 入力テーブル ==========
st.markdown("### ② ライバー情報の入力（デフォルトで荒沢＋ライバル5人）")
st.caption(
    "・「自分」は荒沢の行だけチェックしてください（複数チェックしないよう注意）。\n"
    "・ナイトは「総数」「既投」を入れると「残り」が自動計算されます。\n"
    "・GOGO/わっしょい/ファイトの「%」はアプリのバーストランキング表示値を入力してください。\n"
    "・表の左下「＋」で行を追加できます。空欄のまま計算してもエラーは出ません。"
)

edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "自分": st.column_config.CheckboxColumn("自分（1人だけ）"),
        "現在ポイント": st.column_config.NumberColumn("現在ポイント", format="localized", min_value=0),
        "確定済みイベラス%": st.column_config.NumberColumn("確定済みイベラス%", format="%.2f", min_value=0.0, step=0.25),
        "GOGO%": st.column_config.NumberColumn("GOGO%", format="%.2f", min_value=0.0, step=0.25),
        "わっしょい%": st.column_config.NumberColumn("わっしょい%", format="%.2f", min_value=0.0, step=0.25),
        "ファイト%": st.column_config.NumberColumn("ファイト%", format="%.2f", min_value=0.0, step=0.25),
    },
    key="editor",
)
st.session_state.df = edited

# ========== ⑤ 計算 ==========
st.markdown("### ③ 計算結果（予想最終ポイント）")

night_keys = ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]
results = []

for _, row in edited.iterrows():
    total_bonus = (
        safe_num(row.get("確定済みイベラス%"))
        + safe_num(row.get("GOGO%"))
        + safe_num(row.get("わっしょい%"))
        + safe_num(row.get("ファイト%"))
    )

    rem = {}
    for k in night_keys:
        total = safe_num(row.get(f"{k}総数"), as_int=True)
        used  = safe_num(row.get(f"{k}既投"), as_int=True)
        rem[k] = max(0, total - used)

    night_pt  = sum(rem[k] * prices[k] for k in night_keys)
    current   = safe_num(row.get("現在ポイント"), as_int=True)
    predicted = current + night_pt * (1 + total_bonus / 100)

    results.append({
        "自分": safe_bool(row.get("自分")),
        "ライバー名": safe_name(row.get("ライバー名")),
        "現在ポイント": current,
        "合計ボーナス%": round(total_bonus, 2),
        "残りメガ": rem["メガ"], "残りぽこ": rem["ぽこ"], "残りミニ": rem["ミニ"],
        "残りプチ": rem["プチ"], "残りベビ": rem["ベビ"],
        "残りナイト素点": int(night_pt),
        "予想最終ポイント": int(predicted),
    })

res_df = pd.DataFrame(results).sort_values("予想最終ポイント", ascending=False).reset_index(drop=True)
res_df.index += 1

self_rows = res_df[res_df["自分"] == True]
gap = None
top_point = None

if len(self_rows) > 0:
    my_point  = int(self_rows.iloc[0]["予想最終ポイント"])
    my_rank   = int(self_rows.index[0])
    top_point = int(res_df.iloc[0]["予想最終ポイント"])
    res_df["自分との差分"] = (res_df["予想最終ポイント"] - my_point).astype(int)

    st.success(f"🏅 荒沢の現在予想順位：**{my_rank} 位** / {len(res_df)} 人中")

    gap = top_point - my_point
    if gap > 0:
        st.error(f"⚠️ 1位との差：**{gap:,} pt**")
    elif gap == 0:
        st.warning("⚡ 現在1位と同点です！")
    else:
        st.success(f"✅ 1位を **{abs(gap):,} pt** リードしています！")
else:
    res_df["自分との差分"] = None
    st.info("「自分」にチェックが入っている行がありません。荒沢の行にチェックを入れてください。")

# ---- カンマ表示（確実に効く方法：文字列に変換してから表示）----
display_df = res_df.copy()
for col in ["現在ポイント", "残りナイト素点", "予想最終ポイント", "自分との差分"]:
    display_df[col] = display_df[col].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "-"
    )

st.dataframe(display_df, use_container_width=True)

# ========== ⑥ 逆算ツール（1位に追いつくには） ==========
if len(self_rows) > 0 and gap is not None and gap > 0:
    st.markdown("### ④ 逆算ツール（1位に追いつくにはあと何が必要か）")

    current_my   = int(self_rows.iloc[0]["現在ポイント"])
    my_night_pt  = int(self_rows.iloc[0]["残りナイト素点"])
    my_bonus_pct = float(self_rows.iloc[0]["合計ボーナス%"])

    target = st.number_input(
        "目標ポイント（デフォルトは現在の1位の予想ポイント）",
        value=top_point,
        step=10000,
    )

    col_a, col_b = st.columns(2)

    if my_night_pt > 0:
        needed_bonus_pct = max(0.0, (target - current_my) / my_night_pt * 100 - 100)
        col_a.metric(
            "戦術①：必要な合計ボーナス%（ナイト量は今のまま）",
            f"{needed_bonus_pct:.2f} %",
            delta=f"現在 {my_bonus_pct:.2f}% → あと {max(0, needed_bonus_pct - my_bonus_pct):.2f}pt 上げる必要"
        )
    else:
        col_a.warning("残りナイトが0のため、ボーナス%だけでは目標に届きません。")

    needed_extra_pt = max(0.0, (target - current_my) / (1 + my_bonus_pct / 100) - my_night_pt)
    col_b.metric(
        "戦術②：必要な追加ナイト素点（ボーナス%は今のまま）",
        f"{int(needed_extra_pt):,} pt",
        delta=f"現在の残りナイト素点 {my_night_pt:,} pt に追加"
    )
