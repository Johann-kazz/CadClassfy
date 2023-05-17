import pandas as pd
import ezdxf
import fasttext
import streamlit as st

#ラベル分類する関数
def discriminate_word(texts, classifier):
    labels, probabilities = classifier.predict(texts)
    return labels, probabilities #戻り値：ラベル,Accuary

#dxfからテキストを抽出する関数
def read_dxf_file(dxf, trainingModel):
    """
    DXFファイルを開いて、テキストを抽出する

    Parameters:
        dxf_file (str): DXFファイルのパス
        trainingModel: 学習済みのモデルオブジェクト

    Returns:
        pandas.DataFrame: 抽出したテキストの属性データフレーム
        (handle,内容,ラベル,正確性,レイヤー,X,Y,回転)
    """
    
    #docからtext要素を全て取り出す
    texts = [entity.dxfattribs() for entity in dxf.query('TEXT')]

    textAll=[]
    for i in range(len(texts)) :
        text_data=[]

        text_data.append(texts[i]['handle'])
        text_data.append(texts[i]['text'])
        text_data.append(discriminate_word(texts[i]['text'],trainingModel)[0][0])           #ラベル(種類)
        text_data.append((float)(discriminate_word(texts[i]['text'],trainingModel)[1][0]))  #Accuary
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
    
    return d_text

#@title ####系統番号として正確に認識したデータの確認用関数
#@markdown 系統番号と電線種類のみ

def CreateVerification_dxf(dxf_data, d_text, input_data_file):
    
    # 計算結果をパンダスに返す場合
    #(関数の場合、"apply"or"map"を使い、引数を後ろにつける)  
    #d_text['Kind'] = d_text['Name'].apply(discriminate_word, classifier=model)
    #@markdown 抽出用の正確度の設定
    Accuracy_value = 0.99 #@param
    #@markdown 修正用の正確度の設定
    InAccuracy_value = 0.5 #@param
    # 系統番号のみデータフレーム化
    cir_text = d_text[(d_text['Accuracy'] >= Accuracy_value) & (d_text['Type'] == '__label__CIRNo')] #正解率(Accuracy) 0.99以上
    cir_text = cir_text.reset_index()
    # 電線種類のみデータフレーム化
    Cable_text = d_text[(d_text['Accuracy'] >= Accuracy_value) & (d_text['Type'] == '__label__CABLEType')] #正解率(Accuracy) 0.99以上
    Cable_text = Cable_text.reset_index()

    #不正確データのみを抽出してOutput
    unknown_word = d_text[(d_text['Accuracy'] < InAccuracy_value)] #正解率(Accuracy) 0.99以上
    unknown_word = unknown_word.reset_index()
    unknown_word.to_csv(input_data_file+"Inaccurate.csv")

    #print("CADデータへの色分け準備完了")
    #print("次回学習用"+input_data_file+"Inaccurate.csvを保存しました。")

    #return cir_text, Cable_text

    #@markdown #### 識別した文字の色を変更して保存する
    #@markdown ##### 系統番号:水色(4) 電線種類:赤色(1) 不正確なデータ:黄色(2)
    #entity = dxf_data.entitydb.get(d_text["handle"][3690])

    # 変更したいオブジェクトを選択する
    #系統番号
    for i in range(len(cir_text)):
        entity = dxf_data.entitydb.get(cir_text["handle"][i])
        entity.dxf.color = 4 # 例えば、赤色に変更する場合は、color=1
    #ケーブル種類
    for i in range(len(Cable_text)):
        entity = dxf_data.entitydb.get(Cable_text["handle"][i])
        entity.dxf.color = 1 # 例えば、赤色に変更する場合は、color=1
    #不確定<0.99
    for i in range(len(unknown_word)):
        entity = dxf_data.entitydb.get(unknown_word["handle"][i])
        entity.dxf.color = 2 # 例えば、赤色に変更する場合は、color=1

    # 変更したDXFデータをファイルに書き込む
    #if uploaded_chk == True :
        #input_file = wiring_file
    #dxf_data.saveas("抽出済み.dxf")#+input_data_file)

    #print("色分けたデータ:["+input_data_file+"]保存しました")

    return dxf_data, "抽出済み"+input_data_file , cir_text
    # DXFファイルを閉じる
    #dxf_data.close()