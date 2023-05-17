import streamlit as st
import pandas as pd
import ezdxf
import tempfile
import os.path
import fasttext
import requests
import io, time
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from googleapiclient.discovery import build

from LIB import excel_process as excelep
from LIB import cad_process as cadp

def main():
    # Streamlitアプリの作成
    st.title('系統番号 抽出 in DXF-files')
    
    # 認証情報を読み込む
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = "./GoogleDriveAPI/"+'circit20230511-bf09fa5cb3f8.json'

    
    #try:
        #creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        #st.success("認証情報の読み込みに成功しました")
    #except Exception as e:
        #st.error(f"認証情報の読み込みに失敗しました: {e}")
    
    # Google Drive APIのサービスを初期化
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    
    #Google Driveからファイルを読み込み、pandasのデータフレームとして返す。
    
    service = build('drive', 'v3', credentials=creds)

    # ファイルをダウンロードする
    file_id = "1jQQ66auz3QGCV21IGrZ2to-mJMFPNhIn"
    #学習データ　今治スマート
    #"https://drive.google.com/file/d/1jQQ66auz3QGCV21IGrZ2to-mJMFPNhIn/view?usp=sharing"
    #request = service.files().get_media(fileId=file_id)
    #file = io.BytesIO(request.content)#execute())

    # ファイルのメディアコンテンツを取得するリクエストを作成
    request = service.files().get_media(fileId=file_id)

    # メディアコンテンツをダウンロードして学習データファイルとして保存
    file_path = 'downloaded_model.bin'
    if not os.path.isfile(file_path):
        # ファイルのメディアコンテンツを取得するリクエストを作成
        request = service.files().get_media(fileId=file_id)

        # メディアコンテンツをダウンロードして学習データファイルとして保存
        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                with st.spinner("Training Data Loading..."):
                    # 読み込み処理
                    _, done = downloader.next_chunk()
                    time.sleep(1)  # 仮の読み込み処理

    # FastTextで学習データを読み込む
    model = fasttext.load_model(file_path)
    
    # 読み込み完了後の表示
    st.success("Training Data Loading complete!")
    
    #ローカルにある学習モデルの読み込み 
    #model = fasttext.load_model(file)#"ElecCIR_CLASSIFY.bin")

    # DXFファイルをアップロードする
    uploaded_files = st.file_uploader('DXFファイルをアップロードしてください', type=['dxf'], accept_multiple_files=True)

    #ダウンロードファイル名
    output_file = "output.xlsx"
    download_file=[]  #抽出後のdxfチェック用データ

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            # アップロードされたファイルを読み込む
            dxf_data = uploaded_file.getvalue()

            # テンポラリファイルに保存する
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as f:
                f.write(dxf_data)
                dxf_file_path = f.name
            
            dxf_doc = ezdxf.readfile(dxf_file_path)
            # DXFファイルから文字を抽出する
            df_text = cadp.read_dxf_file(dxf_doc, model)

            st.write(f'{uploaded_file.name}の全ての文字:', df_text)
            
            #系統番号として正確に認識したデータのみでデータフレーム作成し不正確なデータのOutput
            processed_data, downfile_name , CirData = cadp.CreateVerification_dxf(dxf_doc, df_text, dxf_file_path)
            download_file.append(downfile_name)
            processed_data.saveas(f"抽出済み{uploaded_file.name}")
            
            st.write(f'{uploaded_file.name}の系統番号:', CirData)
            
            # Excelファイルに書き込み
            excelep.write_data_to_excel(df_text, output_file, uploaded_file.name)
                
        if os.path.isfile(output_file):
            # ファイルのダウンロード
            with open(output_file, 'rb') as f:
                bytes_data = f.read()
            st.download_button(
                    label=f"{output_file}のダウンロード",
                    data=bytes_data,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # ファイルの削除
            os.remove(output_file)

# アプリケーションを実行する
if __name__ == "__main__":
    main()