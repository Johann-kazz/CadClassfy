import pandas as pd
import openpyxl
import os.path

#excel faileに保存する関数
def write_data_to_excel(data, file_name, sheet_name):
    """
    データをエクセルファイルに保存する
    条件：  同じファイルが存在する場合はシートを追加する
            同じシート名が存在する場合は別名にする
            
    Parameters:
        data (DataFrame): 書き込むデータ
        file_name   : ファイル名

    Returns:
        無し
    """
    
    # Excelファイルが存在するかどうか判定
    if os.path.isfile(file_name):
        # 既存のExcelファイルに書き込む場合
        try:
            with pd.ExcelWriter(file_name, mode='a', engine='openpyxl', if_sheet_exists='error') as writer:
                # シート名を指定してデータを書き込み
                data.to_excel(writer, sheet_name=sheet_name, index=False)
        except ValueError:
            # シートが既に存在する場合は別名に変更して書き込む
            suffix = 1
            while True:
                new_sheet_name = f'{sheet_name} ({suffix})'
                if new_sheet_name not in pd.read_excel(file_name, sheet_name=None):
                    sheet_name = new_sheet_name
                    with pd.ExcelWriter(file_name, mode='a', engine='openpyxl') as writer:
                        data.to_excel(writer, sheet_name=sheet_name, index=False)
                    break
                suffix += 1
    else:
        # 新規のExcelファイルに書き込む場合
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            # シート名を指定してデータを書き込み
            data.to_excel(writer, sheet_name=sheet_name, index=False)
