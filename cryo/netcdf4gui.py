import time

def readfromfiles(parafilename, heatfilename, graphfilename):
    #opens all temp files
    parafile = open(parafilename, 'r')
    heatfile = open(heatfilename, 'r')
    graphfile = open(graphfilename, 'r')
    #reads parameters file and puts info into list
    parameters = parafile.read().strip().split()

    parameters[1] = int(parameters[1])
    parafile.close()

    #reads heatmap data file and puts data into nested list
    #(in the same format as the z list)
    heatmap = []
    for line in heatfile:
        x = line.strip().split()
        for i in range(len(x)):
            x[i] = int(x[i])
        heatmap.append(x)
    heatfile.close()

    #reads graph data file and puts data into list
    graph = graphfile.read().strip().split()
    for i in range(len(graph)):
        graph[i] = int(graph[i])
    graphfile.close()

    return parameters, heatmap, graph


def main():
    while True:
        #calls function with the built in temp file names
        #outputs tuple of the 3 lists created by function
        parameters, heatmap, graph = readfromfiles('tempparameters.txt', 'tempzdata.txt', 'tempgraphdata.txt')

        #prints lists to check code is working correctly
        print('Parameters:')
        print(parameters)
        print('Heatmap:')
        print(heatmap)
        print('Graph:')
        print(graph)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
