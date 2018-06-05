import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

year = 2008
n_topics = 20
topic_columns = ["topic #" + str(i) for i in range(n_topics)]
df_doc_topics = pd.read_csv("Data_out/stackoverflow_topic_coverage_{}.csv".format(year),
                                sep=',', encoding="utf-8")
# plt.boxplot(df_doc_topics[["topic #" + str(i) for i in range(n_topics)]])
melted_df = pd.melt(df_doc_topics, id_vars=['docID'], value_vars=["topic #" + str(i) for i in range(n_topics)])
print(melted_df.head())
sns.boxplot(x="variable", y="value", data=melted_df)
plt.show()
# for i in range(n_topics):
#     plt.boxplot(df_doc_topics["topic #" + str(i)]*100)
#     plt.show()
