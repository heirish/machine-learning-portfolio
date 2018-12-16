from check import StormCheck
import time
import matplotlib.pylab as plt

# storm ui address
uiAddress = "http://192.168.99.100:8080"
# check interval in seconds
interval = 1
# check times
times = 30
# check window, default is 10 miniutes
window = 10 * 60

def plot_dict(dict):
   lists = sorted(dict.items()) # sorted by key, return a list of tuples
   x, y = zip(*lists) # unpack a list of pairs into two tuples
   plt.plot(x, y)
   plt.show()

if __name__ == "__main__":
    checker = StormCheck()
    checked_count = 1
    collected_points = {}
    # collected_points[0] = 0
    while True:
        if checked_count > times:
            break
        res =checker.check_topology_transferred(uiAddress, "topology-3-1544920875", window)
        # res =checker.check_topology_acked(uiAddress, "topology-3-1544920875", window)
        print("tuples: ", res)
        if res >= 0:
            collected_points[checked_count] = int(res/window)
            checked_count += 1
        time.sleep(interval)
    print(collected_points)
    values = collected_points.values()
    average = int(sum(values)/len(values))
    print("throughput: {}/s".format(average))
    plot_dict(collected_points)
