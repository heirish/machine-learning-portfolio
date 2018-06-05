import time
import pandas as pd
from Modules import DataLoader
import importlib
importlib.reload(DataLoader)

# ==========================load tags from xml========================
start_time = time.time()
data = DataLoader.getStackoverflowTags(r"F:\stackoverflow.com-Posts\Posts.xml", -1)
df = pd.DataFrame(data, columns=["docID", "tag"])
df.to_csv("Data_in/tags.csv", columns=["docID", "tag"], sep=',', encoding='utf-8', index=False)
end_time = time.time()
print("load tags done in {} seconds".format(end_time - start_time))


# ============================get tags exclude==================
# get all the un-duplicated tags
# data = []
# for tag in df["tag"].tolist():
#     data_tmp = tag.split(",")
#     data.extend(data_tmp)
# print(data)
# df_tags = pd.DataFrame(data, columns=["tag"])
# df_tags = df_tags.drop_duplicates(["tag"])
# df_tags.to_csv("Data_in/tags_nodup.csv", sep=',', encoding='utf-8', index=False)


def printList(x):
   for item in x:
       print(item)

# df_tags_nodup = pd.read_csv("Data_in/tags_nodup.csv")
# df_tags_ex = pd.read_csv("Data_in/exclude_tags.csv")
# df_tags_left = df_tags_nodup[~df_tags_nodup["tag"].isin(df_tags_ex["tag"])]
# print(df_tags_left.head(5))
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("visual-studio"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.startswith("c++builder"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("xcode"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("android-studio"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("eclipse"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("intellij"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("webstorm"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("phpstorm"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("delphi"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("netbeans"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("jetbrains"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("idea"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("emulator"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("studio"), "tag"].values)

# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("vim"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("emacs"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("sublime"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("notepad"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("gnome"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("markdown"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("jupyter"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("ipython"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("beyondcompare"), "tag"].values)
#
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("gcc"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.startswith("g++"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.startswith("c++"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("clang"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("maven"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("gradle"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("make"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("ndk-build"), "tag"].values)
#
#
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("svn"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("git"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("vss"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("clearcase"), "tag"].values)
#
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("machine"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("min"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("algebra"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("neural"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("linear"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("supervised"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("unsupervised"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("math"), "tag"].values)
#
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("anaconda"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("photoshop"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("wireshark"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("performance"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("test"), "tag"].values)
# printList(df_tags_left.loc[df_tags_left["tag"].str.contains("deploy"), "tag"].values)

# df_tags_left.to_csv("Data_in/tags_left.csv", sep=',', encoding='utf-8', index=False)


# =============== get exclude tags id============================================
start_time = time.time()
df_tags_ex = pd.read_csv("Data_in/exclude_tags.csv")
df["keep"] = 0
for index, row in df.iterrows():
    tags = row["tag"].split(",")
    if df_tags_ex["tag"].isin(tags).any():
        df.set_value(index, "keep", 1)
df_ex_id = df[df["keep"] == 1]
df_ex_id.to_csv("Data_in/exclude_tags_id.csv", columns=["docID", "tag"], sep=',', encoding='utf-8', index=False)
end_time = time.time()
print("get exclude tags id in {} seconds".format(end_time - start_time))
