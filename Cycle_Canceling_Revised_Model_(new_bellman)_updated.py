import copy, sys, csv, os
import csv
import time

import Edmond_Karp_Revised_Model

PORT_INDEX = 2
INVENTORY_INDEX = 1


# Bellman-Ford for detecting negative cycles for use in Cycle-Cancelling algorithm
# if no negative cycles, return None
def bellman_ford(graph, source):
    # number of vertices
    n = len(graph)

    # initialize output arrays
    dist = [sys.maxsize for i in range(n)]
    prev = [-1 for i in range(n)]
    dist[source] = 0
    # prev[source] = source

    # do |V| - 1 relaxations
    for i in range(n - 1):
        for u in range(n):
            for v in graph[u].keys():
                # Set every entry in set of distance to infinity
                tempdist = sys.maxsize
                # if dist[u] != sys.maxint:
                if dist[u] != sys.maxsize:
                    tempdist = dist[u] + graph[u][v][1]
                if dist[v] > tempdist:
                    dist[v] = tempdist
                    prev[v] = u

    # find and return a cycle as a list of pairs of vertices
    cycle = []
    for u in range(n):
        for v in graph[u].keys():
            if dist[v] > dist[u] + graph[u][v][1]:

                C = v
                for i in range(n):
                    C = prev[C]
                v = C
                # temp = v
                while True:
                    cycle.append(v)
                    if v == C and len(cycle) > 1:
                        break
                    v = prev[v]
                cycle.reverse()
                final_cycle = []
                for index in range(len(cycle) - 1):
                    final_cycle.append((cycle[index], cycle[index + 1]))

                # temp = (u, v)
                # while temp not in cycle:
                #     cycle.append(temp)
                #     temp = (prev[temp[0]], temp[0])
                # while temp not in cycle:
                #     cycle.append(temp)
                #     # temp = (prev[temp[0]], temp[0])
                #     temp = prev[temp]
                # print("\nNegative cycle is:\n", cycle)
                print("\nNegative cycle is:\n", final_cycle)
                # return cycle
                return final_cycle
    # no negative cycles
    return None


# Cycle-Cancelling algorithm solves min cost max flow
# after finding a suitable maxflow, fixes it to minimal cost by augmenting along
# the negative cost cycles
# Returns the maxflow, cost, and the assignment as a dictionary
# the assignment is given as a dictionary; it assumes a bipartite graph,
# even though the algorithm works for general networks
def cycle_cancel(G, source, sink):
    # number of vertices
    n = len(G)

    # find feasible maxflow
    F, maxflow, matching = Edmond_Karp_Revised_Model.edmonds_karp(G, source, sink)

    # convert flow graph the from the maxflow to a residual graph
    # remove used flow edges in F
    for u in range(n):
        for v in G[u].keys():
            if F[u][v][0] > 0:
                # F[u][v] = (0, 0)
                if u == sink + 1:
                    F[u][v] = (G[u][v][0] - F[u][v][0], 0)
                else:
                    F[u][v] = (G[u][v][0] - F[u][v][0], G[u][v][1])

    # add unused edges from G to F
    for u in range(n):
        for v in G[u].keys():
            if F[v][u] == (0, 0):
                F[u][v] = G[u][v]
    # convert now residual graph F into list of dicts
    resG = [{} for i in range(n)]
    for u in range(n):
        for v in range(n):
            if F[u][v] != (0, 0):
                resG[u][v] = (abs(F[u][v][0]), F[u][v][1])

    # use Bellman-Ford to find cycles reachable from sink in residual graph
    # augment along this cycle and keep doing so until no more cycles
    while True:
        cycle = bellman_ford(resG, sink)
        if not cycle:
            break
        # smallest capacity of the cycle
        flow = min(resG[u][v][0] for u, v in cycle)
        # augment along cycle, updating flow graph and TODO residual graph
        for u, v in cycle:
            # update residual graph
            temp = resG[u][v]
            # update reverse edge
            if u in resG[v].keys():
                resG[v][u] = (resG[v][u][0] + flow, resG[v][u][1])
            else:
                resG[v][u] = (flow, -resG[u][v][1])
            # update forward edge
            if temp[0] == flow:
                # remove edge if no more capacity
                del resG[u][v]
            else:
                resG[u][v] = (resG[u][v][0] - flow, resG[u][v][1])

    Total_cost = 0
    Trans_cost = 0
    Invent_cost = 0
    print("\nFlow is: ")
    for u in range(n):
        for v in resG[u].keys():
            edge = resG[u][v]
            if edge[1] < 0:
                print((v, u), ":", (edge[0], abs(edge[1])))
                # Total_cost += (edge[0]) * (abs(edge[1]))
                # if v == 1:
                if v == PORT_INDEX:
                    Trans_cost += (edge[0]) * (abs(edge[1]))
                # if v == 8:
                if v == INVENTORY_INDEX:
                    Invent_cost += (edge[0]) * (abs(edge[1]))

                Total_cost = Trans_cost + Invent_cost

    return maxflow, Total_cost, Trans_cost, Invent_cost


#######################################################
# I/O
if __name__ == '__main__':
    start = time.time()
    # csv_f = csv.reader(open('Network_Revised_Model_20depots.csv'))
    # csv_f = csv.reader(open('converted_file.csv'))
    csv_f = open('converted_file_week1.csv')
    # csv_f = open('converted_file_500depots.csv')

    # problem = next(csv_f)[0].lower()
    problem = csv_f.readline().lower().strip()
    # csv file does not correctly indicate stable marriage or
    # hospital resident as the problem to be solved
    if problem != "flow graph":
        print("The problem indicated in graph.csv is not min cost max flow\n")
        print("Exiting to menu.")
        os.system("python menu.py")

    # numVertices = int(next(csv_f)[0])
    numVertices = int(csv_f.readline().strip())
    # initialize graph
    graph = [{} for i in range(numVertices)]
    # vertexnames = next(csv_f)[0].split(' ')
    vertexnames = csv_f.readline().strip().split(' ')

    # sink
    for i in range(numVertices):
        # vertexname = next(csv_f)[0]
        vertexname = csv_f.readline().strip()
        vertexindex = vertexnames.index(vertexname)
        # s1 = next(csv_f)[0]
        # s2 = next(csv_f)[0]
        # s3 = next(csv_f)[0]
        s1 = csv_f.readline().strip()
        s2 = csv_f.readline().strip()
        s3 = csv_f.readline().strip()
        neighborindices = [vertexnames.index(elt) for elt in s1.split(' ')]
        neighborcaps = [int(elt) for elt in s2.split(' ')]
        neighborcosts = [int(elt) for elt in s3.split(' ')]
        for v in range(len(neighborindices)):
            graph[vertexindex][neighborindices[v]] = (neighborcaps[v], neighborcosts[v])

    # assume source and sink already added, last two vertices
    source = 0
    # sink = 7
    sink = numVertices - 1

    maxflow, Total_cost, Trans_cost, Invent_cost = cycle_cancel(graph, source, sink)
    # maxflow, cost = cycle_cancel(graph, source, sink)
    print("\nSolution:")
    print("Optimal flow cost value (Total cost) = $%i" % Total_cost)
    print("Transportation cost = $%i" % Trans_cost)
    print("Inventory cost at depot = $%i" % Invent_cost)
    # print("Assignment:")
    # for v in assignment.keys():
    # print([vertexnames[u] for u in assignment[v]])
    # print("assigned to: %s" % vertexnames[v])
    end = time.time()
    exec_time = end - start
    print(f"Execution time: {exec_time} seconds")
