import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pococha甲子園 予想最終ポイント計算", layout="wide")
st.title("🏆 Pococha甲子園 予想最終ポイント計算ツール")

# ---------- ① ナイト単価設定（必ず実際の値に書き換えてください） ----------
st.markdown("### ① ナイト1個あたりのポイント単価")
st.warning(
    "⚠️ 以下はあくまで仮の初期値です。実際の枠でナイトをタップした際に表示される"
    "「このアイテムで◯pt応援」の数値を確認し、必ず正しい値に書き換えてください。"
)
c1, c2, c3, c4, c5 = st.columns(5)
pt_mega  = c1.number_input("メガナイト単価",  value=33333, step=100)
pt_poko  = c2.number_input("ぽこナイト単価",  value=11111, step=100)
pt_mini  = c3.number_input("ミニナイト単価",  value=3333,  step=100)
pt_puchi = c4.number_input("プチナイト単価",  value=1111,  step=100)
pt_baby  = c5.number_input("ベビナイト単価",  value=333,   step=100)

prices = {"メガ": pt_mega, "ぽこ": pt_poko, "ミニ": pt_mini, "プチ": pt_puchi, "ベビ": pt_baby}

# ---------- ② ライバー情報テーブル ----------
st.markdown("### ② ライバー情報の入力")
st.caption("各ナイトの「総数」「既投」を入れると、「残り（未投下）」は自動計算されます。"
           "「残り」だけにボーナス倍率がかかります。")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([
        {
            "自分": True, "ライバー名": "自分",
            "現在ポイント": 0, "確定済みイベラス%": 0.0,
            "GOGO個数": 0, "GOGO%": 0.0,
            "わっしょい個数": 0, "わっしょい%": 0.0,
            "ファイト個数": 0, "ファイト%": 0.0,
            "メガ総数": 0, "メガ既投": 0,
            "ぽこ総数": 0, "ぽこ既投": 0,
            "ミニ総数": 0, "ミニ既投": 0,
            "プチ総数": 0, "プチ既投": 0,
            "ベビ総数": 0, "ベビ既投": 0,
        },
        {
            "自分": False, "ライバー名": "ライバルA",
            "現在ポイント": 0, "確定済みイベラス%": 0.0,
            "GOGO個数": 0, "GOGO%": 0.0,
            "わっしょい個数": 0, "わっしょい%": 0.0,
            "ファイト個数": 0, "ファイト%": 0.0,
            "メガ総数": 0, "メガ既投": 0,
            "ぽこ総数": 0, "ぽこ既投": 0,
            "ミニ総数": 0, "ミニ既投": 0,
            "プチ総数": 0, "プチ既投": 0,
            "ベビ総数": 0, "ベビ既投": 0,
        },
    ])

edited = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "自分": st.column_config.CheckboxColumn("自分（1人だけチェック）"),
    },
    key="editor",
)
st.session_state.df = edited

# ---------- ③ 計算結果 ----------
st.markdown("### ③ 計算結果（予想最終ポイント）")

night_keys = ["メガ", "ぽこ", "ミニ", "プチ", "ベビ"]
results = []

for _, row in edited.iterrows():
    total_bonus = (
        row["確定済みイベラス%"] + row["GOGO%"] + row["わっしょい%"] + row["ファイト%"]
    )

    rem = {}
    for k in night_keys:
        total = row.get(f"{k}総数", 0) or 0
        used  = row.get(f"{k}既投", 0) or 0
        rem[k] = max(0, total - used)  # ここが「残り」の自動計算部分

    night_pt = sum(rem[k] * prices[k] for k in night_keys)
    predicted = row["現在ポイント"] + night_pt * (1 + total_bonus / 100)

    results.append({
        "自分": row["自分"],
        "ライバー名": row["ライバー名"],
        "合計ボーナス%": round(total_bonus, 2),
        "残りメガ": rem["メガ"], "残りぽこ": rem["ぽこ"], "残りミニ": rem["ミニ"],
        "残りプチ": rem["プチ"], "残りベビ": rem["ベビ"],
        "残りナイト素点": int(night_pt),
        "予想最終ポイント": int(predicted),
    })

res_df = pd.DataFrame(results).sort_values("予想最終ポイント", ascending=False).reset_index(drop=True)

self_rows = res_df[res_df["自分"] == True]
if len(self_rows) > 0:
    my_point = self_rows.iloc[0]["予想最終ポイント"]
    res_df["自分との差分"] = res_df["予想最終ポイント"] - my_point
    my_rank = res_df.index[res_df["自分"] == True][0] + 1
    st.success(f"現在の予想順位：{my_rank} 位 / {len(res_df)} 人中")
else:
    res_df["自分との差分"] = None
    st.info("「自分」にチェックが入っている行がありません。上の表でチェックしてください。")

st.dataframe(res_df, use_container_width=True)
