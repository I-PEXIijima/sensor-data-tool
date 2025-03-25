import streamlit as st
import pandas as pd
import chardet
import io

st.title("CSV統合＆平均計算ツール")
st.write("複数のCSVファイルをアップロードすると、処理後にExcel形式でダウンロードできます。")

uploaded_files = st.file_uploader("CSVファイルをアップロード（複数選択可）", type="csv", accept_multiple_files=True)

if uploaded_files:
    process_btn = st.button("処理実行")

    if process_btn:
        dataframes = []

        for uploaded_file in uploaded_files:
            # エンコーディング検出
            raw = uploaded_file.read()
            encoding = chardet.detect(raw)['encoding']
            uploaded_file.seek(0)

            # CSV読み込み（6行スキップ）
            df = pd.read_csv(uploaded_file, encoding=encoding, skiprows=6)

            # Temp や Humi を含む列を削除
            df = df.loc[:, ~df.columns.str.contains("Temp|Humi", case=False)]

            # 時刻列を保持
            time_col = df.iloc[:, 0]

            # 数値データのみ抽出
            numeric_df = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
            numeric_df.insert(0, 'Time', time_col)

            dataframes.append(numeric_df)

        # 平均計算
        time_col = dataframes[0]['Time']
        average_df = sum(df.iloc[:, 1:] for df in dataframes) / len(dataframes)
        result_df = pd.concat([time_col, average_df], axis=1)

        # Excel出力
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False, sheet_name='平均結果')
        output.seek(0)

        st.success("処理が完了しました。以下からダウンロードしてください👇")
        st.download_button(
            label="📥 Excelファイルをダウンロード",
            data=output,
            file_name="統合結果_平均.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
