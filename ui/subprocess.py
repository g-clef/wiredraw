import configparser
from multiprocessing import Process, Lock
from collections import defaultdict
from typing import Tuple

import requests
import graph_tool


class GraphManager(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parser = configparser.ConfigParser()
        config = parser.read("wiredraw.conf")
        self.server = config["Server"]['URL']
        self.events_url = f"{self.server}/events/list"
        self.details_url = f"{self.server}/details"
        self.timeframe_url = f"{self.server}/stats"
        self.min_buffer = config["UI"]["buffer"]
        self.graphs, diffs = self.initialize_graphs()
        self.present_time = None
        self.time_lock = Lock()
        self.graph_lock = Lock()

    def set_time(self, new_time):
        with self.time_lock:
            self.present_time = new_time
        return True

    def get_time(self):
        with self.time_lock:
            return self.present_time

    def initialize_graphs(self):
        graphs = defaultdict(graph_tool.Graph)
        diffs = defaultdict(Tuple)
        time = self.get_time()
        for counter in range(time, time + 10):
            graphs[time] = graph_tool.Graph()
            diffs[time] = ([], [])
        return graphs, diffs

    def load_graph(self, time):
        url = self.events_url + f"/{time}"
        response = requests.get(url).json()
        nodes = defaultdict(set)
        node_props = defaultdict(list)
        edge_props = defaultdict(list)
        for event in response:
            # each event will be:
            #     source_ip: str
            #     dest_ip: str
            #     zeek_id: str
            #     total_bytes: int  # in bytes + out bytes
            #     direction: int  # in bytes - out bytes
            nodes[event['source_ip']].add(event['dest_ip'])
        new_graph = graph_tool.Graph(nodes)
        # TODO: set edge and node properties here
        if (time-1) in self.graphs:
            diffs = self._diff_graphs(new_graph, self.graphs[time-1])
        else:
            diffs = None
        # TODO: layout
        return new_graph, diffs

    def _update_graphs(self):
        present_time = self.get_time()
        if present_time not in self.graphs:
            # we're outside the range of all the graphs we have, start over.
            self.graphs, self.diffs = self.initialize_graphs()
            for time in range(present_time, present_time + self.min_buffer):
                with self.graph_lock:
                    self.graphs[time], self.diffs[time] = self.load_graph(time)
        else:
            # make sure we have enough forward buffer
            times = sorted(list([int(key) for key in self.graphs.keys()]))
            if times[-1] - present_time < self.min_buffer:
                # we need to grab a few more graphs from the backend
                for time in range(times[-1] + 1, times[-1] + self.min_buffer):
                    with self.graph_lock:
                        self.graphs[time], self.diffs[time] = self.load_graph(time)

    def get_graph_diff(self, time):
        with self.graph_lock:
            if time not in self.diffs:
                return False
            return self.diffs[time]

    def get_graph(self, time):
        with self.graph_lock:
            if time not in self.graphs:
                return False
            return self.graphs[time]

    def get_node_details(self, node):
        # TODO: query backend for node details, return them
        pass

    def get_edge_details(self, edge):
        # TODO: query backend for edge details, return them
        pass

    def prune_graphs(self):
        # TODO: check the size of self.graphs and self.diffs, prune if it's too big
        pass

    def update_properties(self):
        # TODO: get properties of set of graphs from server
        pass

    def run(self):
        # TODO: event loop that starts up, gets graph properties, and calls prune periodically
        pass
