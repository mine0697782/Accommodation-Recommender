import pandas as pd



data = pd.read_excel("dataset/1.xls")
# data = pd.read_excel("merged.xlsx")

for i in range(2,20):
    x = pd.read_excel(f"dataset/{i}.xls")
    data.

print(type(data))
print(data)