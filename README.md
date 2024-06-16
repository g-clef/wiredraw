# wiredraw
drawing zeek logs of network traffic with panda3d

UI:
   * Panda3d for the game engine
   * Have scrubber interface at the bottom that starts ticker which updates the time on a periodic basis and triggers update queries to backend. 
     * When in "Play" mode, makes query to backend every <x> seconds, gets results, compares to existing graph and adds/removes nodes as necessary.
     * When in fast-forward/rewind/scrub mode, makes query when possible, ignores previous layout?
   * Has periodic background thread that queries the server for available timestamp ranges, etc.
   * IPs are spheres, connections are arrowed lines.
   * Thicker lines for more data in connection
   * Click on nodes for information about node (DNS resolutions, connection counts, etc)
   * Click on edges for information about connection (protocol, bytes, decodes, etc). If more than one protocol decode available, tile them one after another.
   * Has setup page to log into backend server
   * Stretch goal: draw histogram across scrubber timeline to show total amount of traffic
    Architecture: 
     * Main process and subprocess
     * Subprocess handles connecting to backend, collecting graph data, offering interface to UI
     * main process:
       * draws graph
       * takes user input for view of graph
       * takes user input for present time (offers "play" button to automatically tick time forward)
       * owns the "present time" from the point of view of the graph  
       * updates the subprocess with present time
       * queries subprocess as time moves forward to get diffs of graph
       * Graphs full graph each 30 seconds to ensure sync
     * Subprocess:
       * Manages a buffer forward and backward of the state of the graph
       * queries backend to build buffer 
       * Builds graphs of each event 
       * offers full graph and diff methods for each second going forward
       * does layout of graph, layout included with diffs and full graph
       * handles getting details of an edge or node if the user clicks on it
       * queries backend to collect present stats of the graph (allowed times, etc)

Backend:
  * Backed by Redis server
  * Information storage keys:
    * timestamp keys are json with the list of active connections at that point and an integer of the length. Do in <x> second chunks. 
      * Format: `<epoch_timestamp>:  set("xhe8db", "d7ldy6a", ...)`
    * connection keys are json with source/dest/size keys as well as key names for conn/dns/etc detail entries
      * Format: `"xhe8db": {"conn: "xhe8db.conn", "http": "xhe8db.http", "ssl": "xhe8db.ssl"}`
    * detail entries contain the full set of information from the bro log for that particular entry
      * Format: `"xhe8db.http": {"url": "/", ...} `
  * server has endpoint that takes POSTS from zeek log reader system, writes various keys with timestamps
    * handle situation where dns.log gets read before conn.log by only writing the timestamp entry from the 
conn.log input, not any of the others...so data will reach redis, but not be visible until conn.log parsing catches
up
  * server has endpoint to log in from ui, and way to accept token auth for zeek reader.
  * server has endpoint to query timestamp range and details of graph
  * server has endpoint to query active connections at a given time (will answer with any entry within +- chunktime/2).
  * server has endpoint to query details of node or edge when clicked on.
  * Stretch goal: generate size histogram

DataCollectors:
  * Have token that allows them to post to backend
  * Run one thread (or one worker, dunno) per zeek log
  * puts one line at a time (allow bulk?) to server, does not parse them, but puts to different url per
log type. So, put to `/logs/dns` for dns.log, `/logs/conn` for conn.log, etc.