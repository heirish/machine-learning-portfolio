import time
import pandas as pd

from Modules import DataLoader
import importlib
importlib.reload(DataLoader)

df_exclude_titles = pd.read_csv("Data_in/exclude_titles_id.csv")
df_exclude_tags = pd.read_csv("Data_in/exclude_tags_id.csv")
# load data from XML, id is string type
EXCLUDE_IDS = df_exclude_titles.docID.astype(str).tolist()
EXCLUDE_IDS.extend(df_exclude_tags.docID.astype(str).tolist())

start_time = time.time()
df = DataLoader.loadStackoverflowFromXML(r"F:\stackoverflow.com-Posts\Posts.xml", 100000)
print(df.shape)
df = df[~df["docID"].isin(EXCLUDE_IDS)]
print(df.shape)
end_time = time.time()
print("loaded data in {} seconds.".format(end_time - start_time))
# df.to_csv("Data_in/titles.csv", columns=["docID", "title"], sep=',', encoding='utf-8', index=False)
df["creationdate"] = pd.to_datetime(df["creationdate"])
df["creationyear"] = df["creationdate"].dt.year
for year in df["creationyear"].unique():
    df[df["creationyear"] == year].to_csv("Data_in/Posts_{}.csv".format(year), columns=DataLoader.KEEP_FIELDS, sep=',', encoding='utf-8', index=False)
