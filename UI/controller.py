import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

        self._fermataPartenza = None
        self._fermataArrivo = None

    def handleCreaGrafo(self,e):
        self._model.buildGraph()
        nNodes = self._model.getNumNodes()
        nEdges = self._model.getNumEdges()

        self._view.lst_result.controls.clear()
        self._view.lst_result.controls.append(ft.Text("Grafo creato correttamente"))
        self._view.lst_result.controls.append(ft.Text(f"Il grafo ha {nNodes} nodi."))
        self._view.lst_result.controls.append(ft.Text(f"Il grafo ha {nEdges} archi."))
        self._view._btnCalcola.disabled = False
        self._view.update_page()

    def handleCreaGrafoPesato(self, e):
        self._model.buildGraphPesato()
        nNodes = self._model.getNumNodes()
        nEdges = self._model.getNumEdges()
        archiPesoMaggiore = self._model.getArchiPesoMaggiore()

        self._view.lst_result.controls.clear()
        self._view.lst_result.controls.append(ft.Text("Grafo pesato creato correttamente."))
        self._view.lst_result.controls.append(ft.Text(f"Il grafo ha {nNodes} nodi."))
        self._view.lst_result.controls.append(ft.Text(f"Il grafo ha {nEdges} archi."))
        # for u, v, peso in archiPesoMaggiore:
        #     self._view.lst_result.controls.append(ft.Text(f"{u} - {v} - {peso}"))
        self._view._btnCalcola.disabled = False
        self._view._btnCalcolaPercorso.disabled = False
        self._view.update_page()

    def handleCercaRaggiungibili(self,e):
        if self._fermataPartenza is None:
            self._view.lst_result.controls.clear()
            self._view.lst_result.controls.append(ft.Text("Attenzione, selezionare la fermata di partenza!"))
            self._view.update_page()
            return
        # visited = self._model.getBFSNodes(self._fermataPartenza)  # il source sarà la fermata di partenza che seleziona l'utente dal dd
        visited = self._model.getDFSNodes(self._fermataPartenza)  # il source sarà la fermata di partenza che seleziona l'utente dal dd
        self._view.lst_result.controls.clear()
        self._view.lst_result.controls.append(ft.Text(f"Dalla stazione {self._fermataPartenza} posso raggiungere {len(visited)} stazioni."))
        for v in visited:
            self._view.lst_result.controls.append(ft.Text(v))
        self._view.update_page()

    def handlePercorso(self,e):
        if self._fermataPartenza is None or self._fermataArrivo is None:
            self._view.lst_result.controls.clear()
            self._view.lst_result.controls.append(ft.Text("Attenzione, selezionare le due fermate!"))
            self._view.update_page()
            return

        totTime, path = self._model.getBestPath(self._fermataPartenza, self._fermataArrivo)
        if path == []:  # se il percorso non esiste, ma in questo caso non è possibile perchè il grafo è connesso
            self._view.lst_result.controls.clear()
            self._view.lst_result.controls.append(ft.Text("Percorso no trovato!"))
            self._view.update_page()
            return

        self._view.lst_result.controls.clear()
        self._view.lst_result.controls.append(ft.Text("Percorso trovato!"))
        self._view.lst_result.controls.append(ft.Text(f"Il cammino più breve fra {self._fermataPartenza} "
                                                      f"e {self._fermataArrivo}"
                                                      f"impiega {totTime} minuti"))

        for p in path:
            self._view.lst_result.controls.append(ft.Text(f"{p}"))

        self._view.update_page()


    def loadFermate(self, dd: ft.Dropdown()):  # per riempire i dropdown
        fermate = self._model.fermate

        if dd.label == "Stazione di Partenza":
            for f in fermate:
                dd.options.append(ft.dropdown.Option(text=f.nome,
                                                     data=f,
                                                     on_click=self.read_DD_Partenza))  # -> modo per recuperare l'oggetto selezionato
        elif dd.label == "Stazione di Arrivo":
            for f in fermate:
                dd.options.append(ft.dropdown.Option(text=f.nome,
                                                     data=f,
                                                     on_click=self.read_DD_Arrivo))

    def read_DD_Partenza(self,e):
        print("read_DD_Partenza called ")
        if e.control.data is None:
            self._fermataPartenza = None
        else:
            self._fermataPartenza = e.control.data

    def read_DD_Arrivo(self,e):
        print("read_DD_Arrivo called ")
        if e.control.data is None:
            self._fermataArrivo = None
        else:
            self._fermataArrivo = e.control.data
