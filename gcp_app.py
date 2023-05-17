import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io, time
import pandas as pd

# 認証情報を読み込む
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = "./GoogleDriveAPI/"+'circit20230511-bf09fa5cb3f8.json'

"""
#try:
    #creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #st.success("認証情報の読み込みに成功しました")
#except Exception as e:
    #st.error(f"認証情報の読み込みに失敗しました: {e}")
"""

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def read_file_from_drive(file_id):
    """
    Google Driveからファイルを読み込み、pandasのデータフレームとして返す。
    """
    service = build('drive', 'v3', credentials=creds)

    # ファイルをダウンロードする
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO(request.execute())
    
    # ファイルをpandasのデータフレームとして読み込む
    #df = pd.read_csv(file)
    df= type(file)

    return df

# Google Driveからファイルを読み込むためのコード
st.title('Google Driveからファイルを読み込む')

# ファイルIDを入力する
#file_id = st.text_input('Google DriveのファイルIDを入力してください')

file_id = "1jQQ66auz3QGCV21IGrZ2to-mJMFPNhIn"

# ファイルを読み込む
if file_id:
    try:
        # スピナーを表示する
        st.spinner("読み込み中...")
        df = read_file_from_drive(file_id)
        st.write(df)
        # スピナーを非表示にする
        st.success("処理が完了しました")
    except:
        st.error('ファイルを読み込めませんでした')



# アップロードされたファイルを加工するためのコード
st.title('アップロードされたファイルを加工する')

# ファイルをアップロードする
uploaded_file = st.file_uploader("ファイルをアップロードしてください", type=['csv'])

# ファイルを読み込む
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write('アップロードされたファイル')
        st.write(df)

        # ファイルを加工する
        df['column1'] = df['column1'] * 2
        df['column2'] = df['column2'] * 3

        st.write('加工後のファイル')
        st.write(df)
    except:
        st.error('ファイルを読み込めませんでした')

#https://drive.google.com/file/d/1XNsXkhr-lGQUa1xriA5psPLrPB-OjMgT/view?usp=sharing
#共有の設定を　閲覧者全員にすること
#https://drive.google.com/file/d/1jQQ66auz3QGCV21IGrZ2to-mJMFPNhIn/view?usp=sharing