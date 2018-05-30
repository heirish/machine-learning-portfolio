import pandas as pd

from Modules import DataLoader
import importlib
importlib.reload(DataLoader)

df = DataLoader.loadStackoverflowFromXML(r"F:\stackoverflow.com-Posts\Posts.xml", 1000000)
df["creationdate"] = pd.to_datetime(df["creationdate"])
df["creationyear"] = df["creationdate"].dt.year
for year in df["creationyear"].unique():
    df[df["creationyear"] == year].to_csv("Data_in/Posts_{}.csv".format(year), columns=DataLoader.KEEP_FIELDS, sep=',', encoding='utf-8', index=False)
