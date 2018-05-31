import os
import argparse
import time
import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact

from Modules import HC, DataSource
import importlib
importlib.reload(HC)
importlib.reload(DataSource)


### Clustering:
#### input: a stream of data, and a maxDist and a distance function and cluster level, as parameter
#### cached data: clusters(id + representive log id + log ids) tree
#### output: updated clusters(level of the tree)
c_tree = {0: {}}


# format:level:{node_id:{"pattern":"", "data":[pids], "unmerged":[]}}, the representive_id is the first element id "data", ex.
# c_tree = {
# 0:{0:{"pattern":"", "data":[2,4,6], "unmerged":[]}, 1:{"pattern":"", "data":[3,7,9], "unmerged":[]}, 2:{"pattern":"", "data":[1, 10], "unmerged":[]}},
# 1:{0:{"pattern":"", "data":[1,3], "unmerged":[]}, 1:{"pattern":"", "data":[2], "unmerged":[]}},
# 2:{0:{"pattern":"", "data":[1], "unmerged":[]}}
# }

def loadDataTxt(data_dir):
    filelist = [#"dump_data.txt"#,
                "epa-http.txt"#,
#                "LA-UR-05-7318-failure-data-1996-2005.csv",
#                "sdsc-http.txt"
                 ]
    data = {}
    data_idx = 0
    for file in filelist:
        if data_dir:
            filepath = os.path.join(data_dir, file)
        else:
            filepath = file
        print("reading file {}.".format(filepath))
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                for line in f:
                    data[data_idx] = line
                    data_idx += 1
            except Exception as e:
                print(e)

    return data


def loadDataCSV(data_dir):
    filelist = ["security-Plogs.csv",
                "other-Plogs.csv"
                ]
    data = pd.DataFrame()
    for datafile in filelist:
        dataTmp = pd.read_csv(os.path.join(data_dir, datafile))
        if "body" not in dataTmp.columns:
            continue
        dataTmp = dataTmp[dataTmp["body"].notnull()]
        dataTmp = dataTmp[["body"]]
        data = data.append(dataTmp, ignore_index=True)

    data_dict = data.to_dict(orient='index')
    return {key: (', '.join("{!s}={!r}".format(key1, val1) for (key1, val1) in value.items())) for key, value in
         data_dict.items()}


def show_pattern(level):
    return {node_id: cluster["pattern"] for node_id, cluster in c_tree[level].items()}


def parseParameters():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_data_dir',
        type=str,
        default='data_in/',
        help='Directory to put the input data.'
    )
    parser.add_argument(
        '--output_data_dir',
        type=str,
        default='data_out/',
        help='Directory to put the log data.'
    )
    parser.add_argument(
        '--levels',
        type=int,
        default=11,
        help='levels of pattern tree to train.'
    )
    return parser.parse_known_args()


if __name__ == "__main__":
    FLAGS, unparsed = parseParameters()
    input_data_dir = FLAGS.input_data_dir
    output_data_dir = FLAGS.output_data_dir
    tree_level = FLAGS.levels

    data = loadDataTxt(input_data_dir)
    # data = loadDataCSV(input_data_dir)
    # print("datalen: {}, show first 10 rows:\n{}".format(len(data), list(data.items())[0:10]))

    max_count = 1000
    # use exp simi decay
    init_simi= 0.6 # <==> init_dist =  1- init_simi
    simi_decay_beta = 0.9
    for i in range(tree_level):
        start_time = time.time()
        c_tree[i] = {}
        if i == 0:
            datasource = DataSource.DataSource(data)
            del data
        else:
            data_cluster = {key: cluster["pattern"] for key, cluster in c_tree[i - 1].items()}
            datasource = DataSource.DataSource(data_cluster)
            del data_cluster
        count = 0
        dist = 1 - init_simi * (simi_decay_beta ** i)
        for id, log in datasource.items():
            if i == 0 and 0 < max_count <= count:
                break

            time1 = time.time()
            c_tree[i] = HC.FastClustering(id, datasource, c_tree[i], maxDist=dist)
            time2 = time.time()
            count += 1

            # 当c_tree变大后，单次iteration的时间也会变多,因为要比较的节点变多
            # if  i == 0 and count % 10 == 0:
            #    print("the {}th iter cluster takes {} seconds"
            #          .format(count, time2 - time1))
        c_tree[i] = HC.updatePatterns(datasource, c_tree[i])
        del datasource
        end_time = time.time()
        print("the {}th level, distance {}, takes {} seconds"
              .format(i, dist, end_time - start_time))
    HC.visualizeCtree(c_tree)

    # this can be shown in jupyter
    interact(show_pattern, level=widgets.IntSlider(min=0, max=10, step=1, value=0));
