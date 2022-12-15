import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_excel('table.xlsx', index_col= "Tid(norsk normaltid)")
print (df.dtypes)
df['Middelvind'] = df['Middelvind'].replace('-', 0)
df['Middelvind'] = df['Middelvind'].astype(float)
print(df["Middelvind"].describe())

import seaborn as sns

fig = sns.distplot(df["Middelvind"])
fig.set(xlabel='Wind (m/s)', ylabel='Density')
plt.show()

