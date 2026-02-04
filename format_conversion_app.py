import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="DataRobot Type Assistant", layout="wide")

DR_TYPES = {
    "Numeric (数値)": "float64",
    "Categorical (カテゴリー)": "object",
    "Text (テキスト)": "object",
    "Date (日付)": "datetime64[ns]",
    "Boolean (真偽値)": "bool"
}

def get_dr_type(dtype, col_data):
    d_type_str = str(dtype)
    if "int" in d_type_str or "float" in d_type_str:
        return "Numeric (数値)"
    elif "datetime" in d_type_str:
        return "Date (日付)"
    elif "bool" in d_type_str:
        return "Boolean (真偽値)"
    elif "object" in d_type_str:
        return "Categorical (カテゴリー)" if col_data.nunique() < 50 else "Text (テキスト)"
    return "Categorical (カテゴリー)"

def get_top_values(series, n=3):
    top_vals = series.value_counts().head(n).index.tolist()
    return ", ".join([str(v) for v in top_vals])

st.title("🤖 DataRobot型 比較・一括変換ツール")

col_up1, col_up2 = st.columns(2)
with col_up1:
    file1 = st.file_uploader("CSV 1 (Max 1GB)", type="csv")
with col_up2:
    file2 = st.file_uploader("CSV 2 (Max 1GB)", type="csv")

if file1 and file2:
    if 'df1' not in st.session_state or 'df2' not in st.session_state:
        with st.spinner('データを読み込み中...'):
            def load_csv(file):
                try:
                    return pd.read_csv(file, encoding='utf-8', low_memory=False)
                except UnicodeDecodeError:
                    file.seek(0)
                    return pd.read_csv(file, encoding='cp932', low_memory=False)
            st.session_state.df1 = load_csv(file1)
            st.session_state.df2 = load_csv(file2)

    df1 = st.session_state.df1
    df2 = st.session_state.df2
    common_cols = sorted(list(set(df1.columns) & set(df2.columns)))
    
    diff_data = []
    for col in common_cols:
        dr_t1 = get_dr_type(df1[col].dtype, df1[col])
        dr_t2 = get_dr_type(df2[col].dtype, df2[col])
        if dr_t1 != dr_t2:
            diff_data.append({
                "カラム名": col,
                "CSV 1の型": dr_t1,
                "CSV 1の頻出値": get_top_values(df1[col]),
                "CSV 2の型": dr_t2,
                "CSV 2の頻出値": get_top_values(df2[col])
            })

    if not diff_data:
        st.success("✅ すべての共通カラムの型が一致しています。")
    else:
        st.divider()
        left_col, right_col = st.columns([2, 1], gap="large")

        with left_col:
            st.subheader("⚠️ 型不一致とサンプルデータ")
            # 高さ 600px でスクロール可能なコンテナを作成
            with st.container(height=600):
                diff_df = pd.DataFrame(diff_data)
                st.dataframe(diff_df, use_container_width=True, hide_index=True)

        with right_col:
            st.subheader("🛠 統一設定")
            # 右側も高さ 600px でスクロール可能に
            with st.form("conversion_form"):
                with st.container(height=520): # ボタンのスペースを確保するため少し低めに設定
                    conv_map = {}
                    for diff in diff_data:
                        col_name = diff["カラム名"]
                        selected_dr = st.selectbox(
                            f"変換：{col_name}", 
                            ["変換しない"] + list(DR_TYPES.keys()), 
                            key=f"target_{col_name}"
                        )
                        if selected_dr != "変換しない":
                            conv_map[col_name] = DR_TYPES[selected_dr]
                
                submit_button = st.form_submit_button("変換を実行してダウンロード", use_container_width=True)

        if submit_button:
            if not conv_map:
                st.warning("変換する項目を選択してください。")
            else:
                try:
                    with st.spinner('変換処理中...'):
                        p_df1 = df1.copy()
                        p_df2 = df2.copy()
                        for col, target_dtype in conv_map.items():
                            if target_dtype == "datetime64[ns]":
                                p_df1[col] = pd.to_datetime(p_df1[col], errors='coerce')
                                p_df2[col] = pd.to_datetime(p_df2[col], errors='coerce')
                            elif target_dtype == "float64":
                                p_df1[col] = pd.to_numeric(p_df1[col], errors='coerce')
                                p_df2[col] = pd.to_numeric(p_df2[col], errors='coerce')
                            else:
                                p_df1[col] = p_df1[col].astype(target_dtype)
                                p_df2[col] = p_df2[col].astype(target_dtype)

                        st.success("変換完了！")
                        d1_c, d2_c = st.columns(2)
                        d1_c.download_button(f"CSV 1 保存", p_df1.to_csv(index=False).encode('cp932'), f"dr_fixed_{file1.name}", "text/csv", use_container_width=True)
                        d2_c.download_button(f"CSV 2 保存", p_df2.to_csv(index=False).encode('cp932'), f"dr_fixed_{file2.name}", "text/csv", use_container_width=True)
                except Exception as e:
                    st.error(f"エラー: {e}")
else:
    if 'df1' in st.session_state: del st.session_state.df1
    if 'df2' in st.session_state: del st.session_state.df2
    st.info("2つのCSVファイルをアップロードしてください。")