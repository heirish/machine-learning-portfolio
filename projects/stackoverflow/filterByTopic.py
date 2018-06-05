import time
import argparse
import pandas as pd


def reFilterData(filter_conf, doc_topics):
    keep_topics = filter_conf["keep_topics"]
    keep_threshold = filter_conf["keep_threshold"]
    delete_topics = filter_conf["delete_topics"]
    delete_threshold = filter_conf["delete_threshold"]

    start_time = time.time()
    # filter keep topics, if any of this topics coverage greater than threshold, then keep
    if keep_topics and keep_threshold:
        keep_coverage_colname = ["topic #" + str(i) for i in keep_topics.split(',')]
        doc_topics = doc_topics[(doc_topics[keep_coverage_colname] >= keep_threshold).any(axis=1)]
    # filter delete topics, if any of these topics coverage greater than threshold, then delete
    if delete_topics and delete_threshold:
        delete_coverage_colname = ["topic #" + str(i) for i in delete_topics.split(',')]
        doc_topics = doc_topics[~(doc_topics[delete_coverage_colname] >= delete_threshold).any(axis=1)]
    end_time = time.time()
    print("filter {} rows in {} seconds".format(doc_topics.shape[0], end_time - start_time))

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

    df_filter_conf = pd.read_csv("{}/topic_filter_conf_{}.csv".format(input_dir, year),
                                 sep=',', encoding="utf-8")
    df_doc_topics = pd.read_csv("{}/stackoverflow_topic_coverage_{}.csv".format(output_dir, year),
                                sep=',', encoding="utf-8")
    # TODO: get the statistic description on the df_toc_topics
    keepDocIDs = reFilterData(df_filter_conf, df_doc_topics)

    df_year = pd.read_csv("{}/Topics_{}.csv".format(input_dir, year), sep=',', encoding="utf-8")
    df_year_left = df_year[df_year["docID"].isin(keepDocIDs)]
    df_year_left.to_csv("{}/Topics_{}.csv".format(input_dir, year), sep=',', encoding="utf-8")
    df_year.to_csv("{}/Topics_{}_old.csv".format(input_dir, year), sep=',', encoding="utf-8")
