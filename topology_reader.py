
class TopologyReader:
    def __init__(self):
        self.file = './topology.txt'
        self.node_quantity = 0
        self.adjacency_matrix = []

    def fill_file(self):
        self.adjacency_matrix = []
        with open(self.file) as top:
            for line in top:
                line = line.strip()
                if len(line) == 0:
                    continue

                try:
                    content = [int(i) for i in line.split()]
                    if len(content) == 1:
                        self.node_quantity = content[0]
                        continue

                    self.adjacency_matrix.append(content)
                except ValueError:
                    print("topology.txt contains non numeric values")
                    break


tr = TopologyReader()
tr.fill_file()

