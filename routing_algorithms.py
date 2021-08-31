import numpy as np
class NetworkAlgorithms:
    def __init__(self):
        self.shortest_path = []
        self.current_path = []
        print("Initializing")

    def min_distance(self, dist, queue):
        # Initialize min value and min_index as -1
        minimum = float("Inf")
        min_index = -1

        # from the dist array,pick one which
        # has min value and is till in queue
        for i in range(len(dist)):
            if dist[i] < minimum and i in queue:
                minimum = dist[i]
                min_index = i
        return min_index



    '''Function that implements Dijkstra's single source shortest path
    algorithm for a graph represented using adjacency matrix
    representation
    Reference: https://www.geeksforgeeks.org/printing-paths-dijkstras-shortest-path-algorithm/
    '''

    def link_state_routing(self, graph, destination, src=0):
        self.shortest_path.clear()
        row = len(graph)

        # All distances start with infinite value
        dist = [float("Inf")] * row

        # Shortest path parent nodes
        parent = [-1] * row

        # Distance from initial vertex
        dist[src] = 0
        self.shortest_path.append([src])

        # Add all vertices in queue
        queue = [i for i in range(row)]

        # Find shortest path for all vertices
        while queue:

            # Pick the minimum dist vertex from vertices that are still in the queue
            u = self.min_distance(dist, queue)

            # remove min element
            queue.remove(u)

            # Update distance and parent index of the picked vertex of those in the queue.
            for i in range(row):
                '''Update dist[i] only if it is in queue, there is
                an edge from u to i, and total weight of path from
                src to i through u is smaller than current value of
                dist[i]'''
                if graph[u][i] and i in queue:
                    if dist[u] + graph[u][i] < dist[i]:
                        dist[i] = dist[u] + graph[u][i]
                        parent[i] = u

        # populate the shortest distance path
        self.get_distance_path(dist, parent, src)
        return self.shortest_path[destination], dist[destination]

    # Populates the shortest distance path array
    def get_path(self, parent, j):

        # Base Case : If j is source
        if parent[j] == -1:
            self.current_path.append(j)
            print(j)
            return
        self.get_path(parent, parent[j])
        self.current_path.append(j)
        print(j)

    # A utility function to print
    # the constructed distance
    # array
    def get_distance_path(self, dist, parent, src=0):
        src = src
        print("Vertex \t\tDistance from Source\tPath")
        for i in range(1, len(dist)):
            print("\n%d --> %d \t\t%d \t\t\t\t\t" % (src, i, dist[i])),
            self.get_path(parent, i)
            self.shortest_path.append(self.current_path.copy())
            self.current_path.clear()



    def distance_vector(self):
        print()


my_matrix = [[0, 2, 88], [float('inf'), 1, 2], [3, 5, 2]]
tf = NetworkAlgorithms()
d = tf.link_state_routing(my_matrix, 2)
print(d)

