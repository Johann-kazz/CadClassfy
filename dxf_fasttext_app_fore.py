import streamlit as st
import pandas as pd
import ezdxf
import tempfile
import fasttext

#ラベル分類する関数
def discriminate_word(texts, classifier):
  labels, probabilities = classifier.predict(texts)
  return labels, probabilities #戻り値：ラベル,Accuary

#学習モデルの読み込み 
model = fasttext.load_model("ElecCIR_CLASSIFY.bin")

# Streamlitアプリの作成
st.title('系統番号 抽出 in DXF-files')

# DXFファイルをアップロードする
uploaded_file = st.file_uploader('DXFファイルをアップロードしてください', type=['dxf'])

if uploaded_file is not None:
    # アップロードされたファイルを読み込む
    dxf_data = uploaded_file.getvalue()

    # テンポラリファイルに保存する
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as f:
        f.write(dxf_data)
        dxf_file_path = f.name
    
    # DXFファイルを開いて、レイヤー名を表示する
    dxf = ezdxf.readfile(dxf_file_path)

    #docからtext要素を全て取り出す
    texts = [entity.dxfattribs() for entity in dxf.query('TEXT')]

    textAll=[]
    for i in range(len(texts)) :
        text_data=[]

        text_data.append(texts[i]['handle'])
        text_data.append(texts[i]['text'])
        text_data.append(discriminate_word(texts[i]['text'],model)[0][0])           #ラベル(種類)
        text_data.append((float)(discriminate_word(texts[i]['text'],model)[1][0]))  #Accuary
        text_data.append(texts[i]['layer'])
        text_data.append((int)(texts[i]['insert'][0]))  #文字のX座標
        text_data.append((int)(texts[i]['insert'][1]))  #文字のY座標
        if texts[i].get('rotation') is not None:        #文字の回転を補正
            text_data.append(texts[i]['rotation']%360)
        else :
            text_data.append(0.0)

        textAll.append(text_data)
    
    d_text=pd.DataFrame(textAll)
    d_text.columns = ['handle', 'Name', 'Type', 'Accuracy', 'Layer', 'PosX','PosY','Rotation']
        
    st.write('系統番号:', d_text)
    
    st.write('filename:', uploaded_file.name)

    # Excelファイルに書き込み
    output_file = "output.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        d_text.to_excel(writer, sheet_name=uploaded_file.name)
        
    # ファイルのダウンロード
    with open(output_file, 'rb') as f:
        bytes_data = f.read()
    st.download_button(
            label="ダウンロード",
            data=bytes_data,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )