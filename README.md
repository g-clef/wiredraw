# wiredraw
drawing network traffic with pygame and networkx


## How

Need the following components:
 * some method of packet capture. Prefer to pull logs from zeek, as they'd have metadata to add
 * A networkx graph of the connections between nodes in the traffic identified above
 * A UI that displays the graph visually, and allows users to "fly" through the traffic

## Components

### packet capture

Assume this would be reading zeek logs, or collecdting them from kafka. WOuld prefer to pull http.log, dns.log, conn.log, cert.log.
It would make calls to the networkx graph to add new connections or properties about the connections

### networkx graph

This would possibly be a separate thread, managing the networkx object. It would have methods for adding, removing nodes, as well as dumping the entire
contents of the graph for the UI. It should also have layout methods (I assume...want to have some way to do feedback perhaps...let the ui do layout also?)

Thought: need some way to expire nodes out of the graph. Each node would, I assume have a create_time, and another method here to prune nodes that are too old


### UI

Would call the networkx process to dump the nodes and their positions. Draws them in pygame, calls node position update if user moves things around.

### manager

Calls other child processes, also periodically calls networkx cleanup processes (reap old nodes)

###
