import streamlit as st
import ezdxf
import tempfile
import fasttext

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
    doc = ezdxf.readfile(dxf_file_path)
    layers = doc.layers
    layer_names = [layer.dxf.name for layer in layers]
    st.write('レイヤー名:', layer_names)
