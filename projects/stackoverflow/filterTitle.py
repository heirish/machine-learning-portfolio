import pandas as pd


df = pd.read_csv("Data_in/titles.csv")
print("loading done, shape: {}".format(df.shape))
df["title"] = df["title"].str.lower()
df_how = df.loc[df["title"].str.startswith("how")]
df_how = df_how[df_how["title"].str.contains("fix") == False]
df_how = df_how[df_how["title"].str.contains("resolve") == False]
df_how = df_how[df_how["title"].str.contains("solve") == False]
df_how = df_how[df_how["title"].str.contains("avoid") == False]
df_how = df_how[df_how["title"].str.contains("deal with") == False]
df_how = df_how[df_how["title"].str.contains("correct") == False]
df_how = df_how[df_how["title"].str.contains("handle") == False]
df_how = df_how[df_how["title"].str.contains("diagnose") == False]
df_how = df_how[df_how["title"].str.contains("troubleshoot") == False]
df_how = df_how[df_how["title"].str.contains("prevent") == False]
df_how.to_csv("Data_in/title_how.csv", sep=',', encoding="utf-8", index=False)

df_what = df[df["title"].str.startswith("what")]
df_what = df_what[df_what["title"].str.contains("causing") == False]
df_what = df_what[df_what["title"].str.contains("cause") == False]
df_what = df_what[df_what["title"].str.contains("fix") == False]
df_what.to_csv("Data_in/title_what.csv", sep=',', encoding="utf-8", index=False)

df_when = df[df["title"].str.startswith("when")]
df_when = df_when[df_when["title"].str.contains("causing") == False]
df_when = df_when[df_when["title"].str.contains("cause") == False]
df_when = df_when[df_when["title"].str.contains("error") == False]
df_when = df_when[df_when["title"].str.contains("fail") == False]
df_when = df_when[df_when["title"].str.contains("except") == False]
df_when.to_csv("Data_in/title_when.csv", sep=',', encoding="utf-8", index=False)

df_where = df[df["title"].str.startswith("where")]
df_where.to_csv("Data_in/title_where.csv", sep=',', encoding="utf-8", index=False)

df_compare = df[df["title"].str.contains(" vs.")]
df_compare = df_compare.append(df[df["title"].str.contains("differen")], ignore_index=True)
df_compare.to_csv("Data_in/title_compare.csv", sep=',', encoding="utf-8", index=False)

df_possible = df[df["title"].str.contains("possibl")]
df_possible = df_possible.append(df[df["title"].str.contains("way to")], ignore_index=True)
df_possible = df_possible.append(df[df["title"].str.contains(" usage ")], ignore_index=True)
df_possible = df_possible.append(df[df["title"].str.contains(" use ")], ignore_index=True)
df_possible.to_csv("Data_in/title_possible.csv", sep=',', encoding="utf-8", index=False)

df_should = df[df["title"].str.startswith("should")]
df_should.to_csv("Data_in/title_should.csv", sep=',', encoding="utf-8", index=False)

df_exclude = df_how
df_exclude.append(df_how, ignore_index=True)
df_exclude = df_exclude.append(df_what, ignore_index=True)
df_exclude = df_exclude.append(df_when, ignore_index=True)
df_exclude = df_exclude.append(df_where, ignore_index=True)
df_exclude = df_exclude.append(df_compare, ignore_index=True)
df_exclude = df_exclude.append(df_possible, ignore_index=True)
df_exclude = df_exclude.drop_duplicates(["title"])
df_exclude.to_csv("Data_in/exclude_titles_id.csv", sep=',', encoding="utf-8", index=False)
df_left = df[~df["docID"].isin(df_exclude["docID"])]
df_left.to_csv("Data_in/titles_left.csv", sep=',', encoding="utf-8", index=False)
