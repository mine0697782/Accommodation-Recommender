import pandas as pd
import glob

# 와일드카드 경로를 사용하여 엑셀 파일 목록을 가져옵니다.
file_pattern = '/Users/jmj/Accommodation-Recommender/dataset/*.xls'
excel_files = glob.glob(file_pattern)

# 엑셀 파일 목록을 출력하여 확인합니다.
print("Excel files found:", excel_files)

# 파일이 존재하는지 확인합니다.
if not excel_files:
    raise ValueError("No Excel files found in the directory")

# 각 엑셀 파일을 읽어서 데이터프레임으로 변환한 후 리스트에 저장합니다.
dataframes = []
for file in excel_files:
    try:
        df = pd.read_excel(file)
        dataframes.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

# 데이터프레임들이 잘 저장되었는지 확인합니다.
if not dataframes:
    raise ValueError("No dataframes were created. Check if the Excel files are valid and not empty.")

# 데이터프레임들을 수직으로 이어붙입니다.
combined_dataframe = pd.concat(dataframes, ignore_index=True)

# 모든 문자열 열에 대해 콤마를 개행 문자로 바꿉니다.
combined_dataframe = combined_dataframe.applymap(lambda x: str(x).replace(',', '\n') if isinstance(x, str) else x)

# 결과를 CSV 파일로 저장합니다.
output_csv = '/Users/jmj/Accommodation-Recommender/combined_dataset.csv'
combined_dataframe.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"Combined CSV file saved to {output_csv}")
