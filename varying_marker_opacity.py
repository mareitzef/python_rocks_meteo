# imports
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# sample data in the form of an hourlt
np.random.seed(1234)
tseries = pd.date_range("01.01.2020", "01.04.2020", freq="H")
data = np.random.randint(-100, 100, size=(len(tseries), 3))
df = pd.DataFrame(data=data)
df.columns=list('ABC')
df['C_scaled'] = df['C'].max()/df['C']
df['C_scaled'] = (df['C']-df['C'].min())/(df['C'].max()-df['C'].min())

df = df.sort_values(by=['C_scaled'], ascending=False)

fig=go.Figure()

for ix in df.index:
    d = df.iloc[ix]
    opac = str(d['C_scaled'])
    fig.add_trace(go.Scatter(x=[d['A']], y=[d['B']], showlegend=False,
                             marker=dict(size = 14, color='rgba(100,0,255,'+opac+')',
                                         line=dict(color='rgba(0,0,0,1)', width = 2)))
                            )
    
fig.show()