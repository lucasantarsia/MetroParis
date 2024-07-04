from database.DAO import DAO
import networkx as nx
import geopy.distance

class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph()  # grafo orientato

        self._idMap = {}  # -> Creo un dizionario che ha come chiavi gli id e come valori gli oggetti
        for f in self._fermate:
            self._idMap[f.id_fermata] = f

        self._linee = DAO.getAllLinee()
        self._lineaMap = {}
        for l in self._linee:
            self._lineaMap[l.id_linea] = l


    """COSTRUZIONE DEL GRAFO"""

    def buildGraph(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        self.addEdgeMode3()  # scegliamo uno dei 3 modi per creare il grafo

    def addEdgeMode1(self):
        """Mode 1: doppio loop su nodi e query per ogni arco."""
        # I problemi sono che cicliamo troppo e per ogni nodo facciamo una query
        self._grafo.clear_edges()
        for u in self._fermate:
            for v in self._fermate:
                res = DAO.getEdge(u, v)
                if len(res) > 0:  # se res non è vuoto vuol dire che c'è una connessione
                    self._grafo.add_edge(u, v)
                    # print(f"Added edge between {u} and {v}")

    def addEdgeMode2(self):
        """Mode 2: loop singolo sui nodi e query per identificare i vicini"""
        self._grafo.clear_edges()
        for u in self._fermate:
            vicini = DAO.getEdgeVicini(u)
            for v in vicini:
                v_nodo = self._idMap[v.id_stazA]  # In questo modo mi salvo la stazione di arrivo di v
                self._grafo.add_edge(u, v_nodo)
                # print(f"Added edge between {u} and {v_nodo}")

    def addEdgeMode3(self):
        """Mode 3: unica query che legge tutte le connessioni"""
        self._grafo.clear_edges()
        allConnessioni = DAO.getAllConnessioni()
        # print(len(allConnessioni))  # -> tutte le connessioni sono 1476, di più dei vertici perchè alcuni sono doppi, collegano gli stessi nodi
        for c in allConnessioni:
            u_nodo = self._idMap[c.id_stazP]
            v_nodo = self._idMap[c.id_stazA]
            self._grafo.add_edge(u_nodo, v_nodo)
            # print(f"Added edge between {u_nodo} and {v_nodo}")


    """VISITA DEL GRAFO"""

    # BFS è utile per cercare i cammini minimi
    def getBFSNodes(self, source):  # Metodo per il breadht first source
        edges = nx.bfs_edges(self._grafo, source)  # -> passiamo come parametri il grafo, il source ed eventualmente il limite di profondità
        # questo metodo ritorna una tupla di nodi
        # edges è un generatore:
        visited = []
        for u, v in edges:
            visited.append(v.nome)
        return visited  # -> visited è una lista di tutti i nodi del grafo

    # DFS è utile per cercare la componente connessa, cerca i nodi più velocemente
    def getDFSNodes(self, source):
        edges = nx.dfs_edges(self._grafo, source)
        visited = []
        for u, v in edges:
            visited.append(v)
        return visited


    """ESTENSIONI 1"""

    def buildGraphPesato(self):
        """Questo metodo e del tutto equivalente a buildGraph,
        ma chiama come metodo per aggiungere gli archi "addEdgePesati" """
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        # self.addEdgePesatiLinee()
        self.addEdgePesatiTempo()

    def addEdgePesatiLinee(self):
        """Questo metodo assegna come peso degli edges il numero di linee
        che congiungono i diversi nodi."""
        # Voglio creare archi pesati, dove il peso indica il numero di volte che due archi sono connessi tra di loro
        self._grafo.clear_edges()
        allConnessioni = DAO.getAllConnessioni()
        for c in allConnessioni:
            if self._grafo.has_edge(self._idMap[c.id_stazP], self._idMap[c.id_stazA]):
            # if: c'è già l'arco? Se sì, incremento il peso di 1
                self._grafo[self._idMap[c.id_stazP]][self._idMap[c.id_stazA]]["weight"] += 1
            else:
            # else: allora vuol dire che non l'ho mai aggiunto
                self._grafo.add_edge(self._idMap[c.id_stazP], self._idMap[c.id_stazA], weight=1)

    def getEdgeWeight(self, v1, v2):  # Metodo che ritorna il peso dell'arco dati due nodi
        return self._grafo[v1][v2]["weight"]

    def getArchiPesoMaggiore(self):
        """Print di archi con peso maggiore di 1 (agisce solo sul grafo pesato)"""
        if len(self._grafo.edges) == 0:
            print("Il grafo è vuoto")
            return
        result = []
        edges = self._grafo.edges
        for u, v in edges:
            peso = self._grafo[u][v]["weight"]
            if peso > 1:
                result.append((u, v, peso))
        return result


    """CAMMINI MINIMI"""

    def addEdgePesatiTempo(self):
        """Questo metodo assegna come peso degli edges il tempo di percorrenza
        (basato sulla velocità della linea e sulle posizioni delle fermate)."""
        self._grafo.clear_edges()
        allConnessioni = DAO.getAllConnessioni()
        for c in allConnessioni:
            v0 = self._idMap[c.id_stazP]
            v1 = self._idMap[c.id_stazA]
            linea = self._lineaMap[c.id_linea]
            peso = self.getTraversalTime(v0, v1, linea)

            if self._grafo.has_edge(v0, v1):  # se esiste già l'arco verifico se il tempo è maggiore
                if self._grafo[v0][v1]["weight"] > peso:
                    self._grafo[v0][v1]["weight"] = peso
            else:
                self._grafo.add_edge(v0, v1, weight=peso)

    def getTraversalTime(self, v0, v1, linea):
        p0 = (v0.coordX, v0.coordY)  # -> posizione è in coordinate
        p1 = (v1.coordX, v1.coordY)
        dist = geopy.distance.distance(p0, p1).km  # libreria per calcolare la distanza da due coordinate
        vel = linea.velocita
        tempo = dist/vel * 60  # in minuti
        return tempo

    def getBestPath(self, v0, v1):
        costoTot, path = nx.single_source_dijkstra(self._grafo, v0, v1)
        return costoTot, path


    @property
    def fermate(self):
        return self._fermate

    def getNumNodes(self):
        return len(self._grafo.nodes)

    def getNumEdges(self):
        return len(self._grafo.edges)
