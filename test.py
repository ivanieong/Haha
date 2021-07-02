import pandas as pd
import numpy as np

dd = pd.read_csv('0700.csv')
dd = dd.dropna()
df = dd.reset_index(drop=True)

(row, num_col) = df.shape

a = df['High'].head(60)
b = df['Open'].head(60)

output = []
for i in range(len(b)):
  tmp_array = []
  for j in range(len(a)):
    if ( j >= i ):
      up = ((a[j]/b[i]) - 1) * 100
    else:
      up = 0
    tmp_array.insert(j, up)
    continue
  output.append(tmp_array)
output = np.round_(output, decimals = 2)
print(len(output))
