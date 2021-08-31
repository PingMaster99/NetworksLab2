
class TopologyReader:
    def __init__(self):
        self.file = './topology.txt'
        self.node_quantity = 0
        self.adjacency_matrix = []
        self.nodes = []
        self.fill_file()

    def fill_file(self):
        self.adjacency_matrix = []
        with open(self.file) as top:
            first_line = True
            for line in top:
                if first_line:
                    self.nodes = line.split()
                    self.nodes = [f"{node}@alumchat.xyz" for node in self.nodes]
                    self.node_quantity = len(self.nodes)
                    first_line = False
                    continue

                line = line.strip()
                if len(line) == 0:
                    continue

                try:
                    content = [float(i) for i in line.split()]
                    if len(content) != len(self.nodes):
                        self.nodes = None
                        self.adjacency_matrix = None
                        print("topology.txt contains an adjacency matrix that is not proportional to the number of "
                              "nodes")
                        break
                    self.adjacency_matrix.append(content)

                except ValueError:
                    print("topology.txt contains non numeric values")
                    break


tr = TopologyReader()
tr.fill_file()
print(tr.nodes)
print(tr.adjacency_matrix)
