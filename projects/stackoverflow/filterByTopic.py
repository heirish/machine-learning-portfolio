import os
import time
import argparse
import pandas as pd


def reFilterData(filter_conf, doc_topics):
    start_time = time.time()
    for index, row in filter_conf.iterrows():
        topic_name = row["topic_name"]
        threshold = row["threshold"]
        keep_or_delete = row["keep"]
        if keep_or_delete == 1: # keep
            doc_topics = doc_topics[doc_topics[topic_name] >= threshold]
        else: # delete
            doc_topics = doc_topics[~(doc_topics[topic_name] >= threshold)]

    end_time = time.time()
    print("filtered in {} seconds"
          .format(end_time - start_time))

    return doc_topics["docID"].tolist()


def parseParameters():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_data_dir',
        type=str,
        default='./Data_in',
        help='Directory to put the input data.'
    )
    parser.add_argument(
        '--output_data_dir',
        type=str,
        default='./Data_out',
        help='Directory to put the log data.'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2008,
        help='year of data.'
    )

    return parser.parse_known_args()

if __name__ == "__main__":
    FLAGS, unparsed = parseParameters()
    input_dir = FLAGS.input_data_dir
    output_dir = FLAGS.output_data_dir
    year = FLAGS.year

    already_deleted_file = "{}/deleted_docID_{}.csv".format(input_dir, year)
    posts_bak_file = "{}/Posts_old_{}.csv".format(input_dir, year)
    deleted_posts_file = "{}/Posts_deleted_{}.csv".format(input_dir, year)
    posts_file = "{}/Posts_{}.csv".format(input_dir, year)
    doc_topics_file = "{}/stackoverflow_topic_coverage_{}.csv".format(output_dir, year)
    filter_conf_file = "{}/topic_filter_conf_{}.csv".format(output_dir, year)

    df_filter_conf = pd.read_csv(filter_conf_file, sep=',', encoding="utf-8")
    df_doc_topics = pd.read_csv(doc_topics_file, sep=',', encoding="utf-8")
    keepDocIDs = reFilterData(df_filter_conf, df_doc_topics)
    print("filtered, doc_topics {}, keep {}".format(df_doc_topics.shape[0], len(keepDocIDs)))

    df_year = pd.read_csv(posts_file, sep=',', encoding="utf-8")
    # backup the old file
    try:
        os.replace(posts_file, posts_bak_file)
    except Exception as e:
        print(e)
        df_year.to_csv(posts_bak_file, sep=',', encoding="utf-8", index=False)

    df_year_left = df_year[df_year["docID"].isin(keepDocIDs)]
    df_year_left.to_csv(posts_file, sep=',', encoding="utf-8", index=False)
    print("filtered, before {}, after {}".format(df_year.shape[0], df_year_left.shape[0]))
    del df_year_left

    df_deleted_already = pd.DataFrame(columns=["docID"])
    if os.path.isfile(already_deleted_file):
        df_deleted_already = pd.read_csv(already_deleted_file, sep=',', encoding="utf-8")

    df_year_deleted = df_year[~(df_year["docID"].isin(keepDocIDs))]
    if df_year_deleted.shape[0] > 0:
        df_year_deleted.to_csv(deleted_posts_file, sep=',', encoding="utf-8", index=False)
        print("deleted {}".format(df_year_deleted.shape[0]))
        concat_df = [df_deleted_already, df_year_deleted]
        df_deleted_already = df_deleted_already.append(pd.DataFrame(df_year_deleted["docID"], columns=["docID"]))
        df_deleted_already = df_deleted_already.drop_duplicates(["docID"])
        df_deleted_already.to_csv(already_deleted_file, sep=',', encoding="utf-8", index=False)
    print("already deleted {}".format(df_deleted_already.shape[0]))
