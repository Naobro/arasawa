import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園｜荒沢 予想最終ポイント計算ツール")

# ========== ① 安全な数値変換 ==========
def safe_num(val, as_int=False):
    """None / NaN / 空文字 / 全角 / %付き / カンマ付き などを安全に数値へ変換"""
    if val is None:
        return 0
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return 0
    s = unicodedata.normalize("NFKC", s)  # 全角→半角
    s = s.replace(",", "").replace("%", "").replace("％", "")
    try:
        v = float(s)
        if pd.isna(v):
            return 0
        return int(round(v)) if as_int else v
    except (TypeError, ValueError):
        return 0

def safe_name(val):
    return "" if (val is None or (isinstance(val, float) and pd.isna(val))) else str(val)

def safe_bool(val):
    return bool(val) if (val is not None and not (isinstance(val, float) and pd.isna(val))) else False

# ========== ② ナイト単価（フォームでまとめ、テーブルとは別のsession_stateで独立管理） ==========
st.markdown("### ① ナイト1個あたりのポイント単価")
st.warning(
    "⚠️ 以下は仮の初期値です。実際の枠でナイトをタップした際に表示される"
    "「このアイテムで◯pt応援」の数値に必ず書き換えてください。"
)

if "prices" not in st.session_state:
    st.session_state.prices = {"メガ": 55555, "ぽこ": 11111, "ミニ": 3333, "プチ": 1111, "ベビ": 333}

# ★st.form でまとめることで、「送信」を押すまでは再実行（rerun）が発生しない。
#   これにより、単価をいじっている最中に下のテーブルの編集内容が消える事故を防ぐ。
with st.form("price_form"):
    c1, c2, c3, c4, c5 = st.columns(5)
    p_mega  = c1.number_input("メガ単価",  value=st.session_state.prices["メガ"],  step=100)
    p_poko  = c2.number_input("ぽこ単価",  value=st.session_state.prices["ぽこ"],  step=100)
    p_mini  = c3.number_input("ミニ単価",  value=st.session_state.prices["ミニ"],  step=100)
    p_puchi = c4.number_input("プチ単価",  value=st.session_state.prices["プチ"], step=100)
    p_baby  = c5.number_input("ベビ単価",  value=st.session_state.prices["ベビ"],  step=100)
    if st.form_submit_button("単価を更新"):
        st.session_state.prices = {"メガ": p_mega, "ぽこ": p_poko, "ミニ": p_mini, "プチ": p_puchi, "ベビ": p_baby}

prices = st.session_state.prices

# ========== ③ デフォルトデータ（荒沢＋ライバル5人） ==========
def make_row(is_self, name):
    return {
        "自分": is_self, "ライバー名": name,
        "現在ポイント": 0, "確定済みイベラス%": 0,
        "GOGO個数": 0, "GOGO%": 0,
        "わっしょい個数": 0, "わっしょい%": 0,
        "ファイト個数": 0, "ファイト%": 0,
        "メガ総数": 0, "メガ既投": 0,
        "ぽこ総数": 0, "ぽこ既投": 0,
        "ミニ総数": 0, "ミニ既投": 0,
        "プチ総数": 0, "プチ既投": 0,
        "ベビ総数": 0, "ベビ既投": 0,
    }

if "rival_df" not in st.session_state:
    _rows = [make_row(True, "荒沢")]
    for i in range(1, 6):
        _rows.append(make_row(False, f"ライバル{i}"))
    st.session_state.rival_df = pd.DataFrame(_rows)

# ========== ④ 入力テーブル ==========
st.markdown("### ② ライバー情報の入力")

st.caption(
    "・「自分」は荒沢の行だけチェックしてください。\n"
    "・ナイトは「総数」「既投」を入力すると「残り」が自動計算されます。\n"
    "・％欄は小数も入力できます（例：48.12）。\n"
    "・ポイント・個数欄はカンマなしで入力してください（例：10000000）。\n"
    "・入力後は Enter または Tab キーで確定してください。"
)

edited = st.data_editor(
    st.session_state.rival_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={

        "自分": st.column_config.CheckboxColumn("自分（1人だけ）"),

        "ライバー名": st.column_config.TextColumn(
            "ライバー名",
            width="medium",
        ),

        "現在ポイント": st.column_config.NumberColumn(
            "現在ポイント",
            min_value=0,
        ),

        "確定済みイベラス%": st.column_config.NumberColumn(
            "確定済みイベラス%",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        ),

        "GOGO個数": st.column_config.NumberColumn(
            "GOGO個数（メモ）",
            min_value=0,
        ),

        "GOGO%": st.column_config.NumberColumn(
            "GOGO%",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        ),

        "わっしょい個数": st.column_config.NumberColumn(
            "わっしょい個数（メモ）",
            min_value=0,
        ),

        "わっしょい%": st.column_config.NumberColumn(
            "わっしょい%",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        ),

        "ファイト個数": st.column_config.NumberColumn(
            "ファイト個数（メモ）",
            min_value=0,
        ),

        "ファイト%": st.column_config.NumberColumn(
            "ファイト%",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        ),

        "メガ総数": st.column_config.NumberColumn(
            "メガ総数",
            min_value=0,
        ),

        "メガ既投": st.column_config.NumberColumn(
            "メガ既投",
            min_value=0,
        ),

        "ぽこ総数": st.column_config.NumberColumn(
            "ぽこ総数",
            min_value=0,
        ),

        "ぽこ既投": st.column_config.NumberColumn(
            "ぽこ既投",
            min_value=0,
        ),

        "ミニ総数": st.column_config.NumberColumn(
            "ミニ総数",
            min_value=0,
        ),

        "ミニ既投": st.column_config.NumberColumn(
            "ミニ既投",
            min_value=0,
        ),

        "プチ総数": st.column_config.NumberColumn(
            "プチ総数",
            min_value=0,
        ),

        "プチ既投": st.column_config.NumberColumn(
            "プチ既投",
            min_value=0,
        ),

        "ベビ総数": st.column_config.NumberColumn(
            "ベビ総数",
            min_value=0,
        ),

        "ベビ既投": st.column_config.NumberColumn(
            "ベビ既投",
            min_value=0,
        ),
    },
    key="rival_editor",
)

st.session_state.rival_df = edited

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

display_df = res_df.copy()
for col in ["現在ポイント", "残りナイト素点", "予想最終ポイント", "自分との差分"]:
    display_df[col] = display_df[col].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "-"
    )

st.dataframe(display_df, use_container_width=True)

# ========== ⑥ 逆算ツール ==========
if len(self_rows) > 0 and gap is not None and gap > 0:
    st.markdown("### ④ 逆算ツール（1位に追いつくにはあと何が必要か）")

    current_my   = int(self_rows.iloc[0]["現在ポイント"])
    my_night_pt  = int(self_rows.iloc[0]["残りナイト素点"])
    my_bonus_pct = float(self_rows.iloc[0]["合計ボーナス%"])

    target = st.number_input(
        "目標ポイント（デフォルトは現在の1位の予想ポイント）",
        value=top_point, step=10000, key="target",
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
