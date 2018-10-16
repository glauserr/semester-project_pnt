#!/bin/python3

import plotter as plotter

def getshorteslongestpath(V, E):
	def forward(sender, receiver):
		neighbors = getneighborhood(receiver, E)
		neighbors.remove(sender)
		# print(neighbors)
		# exit()
		if neighbors == []:
			return 1
		else:
			hops = [1 + forward(receiver, n) for n in neighbors]
			return max(hops)

	longestpath = []
	for v in V:
		neighborhood = getneighborhood(v, E)
		# print("node:{}".format(v))
		hops = [forward(v, n) for n in neighborhood]
		# print(hops)
		# print(max(hops))
		longestpath += [max(hops)]

	print(longestpath)
	print(min(longestpath))


def getneighborhood(v, E):
    neighbors = [e[1] for e in E if e[0] == v]
    return neighbors + [e[0] for e in E if e[1] == v]	

if __name__ == '__main__':
	E = [[0, 1],[9,4],[4,7],[4,2],[4,3],[2,8],[1,9],[5,9], [6,0]]
	V = list(range(10))
	plotter.plotgraph(E,V)
	getshorteslongestpath(V,E)
