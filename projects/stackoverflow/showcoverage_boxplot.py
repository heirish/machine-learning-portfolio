import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument(
    '--year',
    type=int,
    default=2008,
    help='year of data'
)
parser.add_argument(
    '--n_topics',
    type=int,
    default=20,
    help='number of topics'
)
FLAGS, unparsed = parser.parse_known_args()

year = FLAGS.year
n_topics = FLAGS.n_topics
topic_columns = ["topic #" + str(i) for i in range(n_topics)]
df_doc_topics = pd.read_csv("Data_out/stackoverflow_topic_coverage_{}.csv".format(year),
                                sep=',', encoding="utf-8")
print(df_doc_topics[topic_columns].describe())
melted_df = pd.melt(df_doc_topics, id_vars=['docID'], value_vars=topic_columns)
print(melted_df.head())
sns.boxplot(x="variable", y="value", data=melted_df)
plt.show()
# for i in range(n_topics):
#     plt.boxplot(df_doc_topics["topic #" + str(i)]*100)
#     plt.show()
