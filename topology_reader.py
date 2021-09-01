# encoding: utf-8
"""
    messenger_account.py
    Authors: Mario Sarmientos, Randy Venegas, Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated August 31, 2021

    Reads a txt file to form a network topology
"""

from constants import SERVER


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
                    self.nodes = [f"{node}{SERVER}" for node in self.nodes]
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

