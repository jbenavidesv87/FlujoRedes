from math import sqrt
from os import system
class Grafo:

    def __init__(self):
        self.nombre = "grafo"
        self.dirigido = False
        self.nodos = [] # un conjunto
        self.pesos = dict() # un mapeo de pesos de aristas
        self.vecinos = dict() # un mapeo

    #def __repr__(self): # https://stackoverflow.com/questions/1984162/purpose-of-pythons-repr
        #return self.__str__()

    #def __str__(self): # https://stackoverflow.com/questions/12448175/confused-about-str-on-list-in-python
        #return "hola"

    def AgregarNodo(self, n):
        self.nodos.append(n)
        if not n in self.vecinos: # vecindad de n
            self.vecinos[n] = set()

    def NodoConId(self, id):
        for n in self.nodos:
            if n.id == id:
                return n
        return None

    def EliminarNodo(self, n):
        temp = self.dirigido
        self.dirigido = False
        self.EliminarVecindades(n)
        self.dirigido = temp
        self.nodos.remove(n)

    def ConectarNodos(self, n1, n2, peso = 1):
        if n1 not in self.nodos:
            self.AgregarNodo(n1)
        if n2 not in self.nodos:
            self.AgregarNodo(n2)
        self.vecinos[n1].add(n2)
        self.pesos[(n1, n2)] = peso
        if not self.dirigido:
            self.vecinos[n2].add(n1) # Si no es dirigido, también debería haber una conexión bivalente
            self.pesos[(n2, n1)] = peso

    def ModificarPesos(self, n, p):
        for v in self.vecinos[n]:
            self.pesos[(n, v)] = p
        if not self.dirigido: # Si no es un grafo dirigido
            for k in list(self.vecinos): # Por cada k nodos que tengan vecindades
                if n in self.vecinos[k]: # Si n está en una de las vecindades de k
                    self.pesos[(k, n)] = p

    def EliminarVecindades(self, n):
        for v in self.vecinos[n]: # Por cada vecino de n
            del(self.pesos[(n, v)]) # Eliminar los pesos entre n y sus vecinos
        self.vecinos[n] = set() # Se eliminan los vecinos de n
        if not self.dirigido: # Si no es un grafo dirigido
            for k in list(self.vecinos): # Por cada k nodos que tengan vecindades
                if n in self.vecinos[k]: # Si n está en una de las vecindades de k
                    del(self.pesos[(k, n)]) # Se eliminan sus pesos
                    self.vecinos[k].remove(n) # Y se remueve dicha vecindad con n

    def Distancia(self, p1, p2):
        d = sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return d

    def DistanciaTotal(self):
        d = 0.0
        for n in self.vecinos:
            for v in self.vecinos[n]:
                d += self.Distancia(n.posicion, v.posicion)
        return d

    def Floyd_Warshall(self):
        d = {} # diccionario de distancias
        for n in self.nodos:
            d[(n, n)] = 0
            for v in self.vecinos[n]: # para vecinos, la distancia es el peso
               d[(n, v)] = self.pesos[(n, v)]
        for intermedio in self.nodos:
            for desde in self.nodos:
                for hasta in self.nodos:
                    di = None
                    if (desde, intermedio) in d:
                        di = d[(desde, intermedio)]
                    ih = None
                    if (intermedio, hasta) in d:
                        ih = d[(intermedio, hasta)]
                    if di is not None and ih is not None:
                        c = di + ih # largo del camino via "i"
                        if (desde, hasta) not in d or c < d[(desde, hasta)]:
                            d[(desde, hasta)] = c # mejora al camino actual
        return d

    def Camino(self, s, t): # construcción de un camino aumentante
        # s : origen
        # t : destino
        cola = [s]
        usados = set()
        camino = dict()
        while len(cola) > 0:
            u = cola.pop(0)
            usados.add(u)
            for (w, v) in self.pesos:
                if w == u and v not in cola and v not in usados:
                    actual = self.vecinos.get((u, v), 0)
                    dif = self.pesos[(u, v)] - actual
                    if dif > 0:
                        cola.append(v)
                        camino[v] = (u, dif)
        if t in usados:
            return camino
        else: # no se alcanzó
            return None

    def Ford_Fulkerson(self, s, t): # algoritmo de Ford y Fulkerson
        if s == t:
            return 0
        maximo = 0
        f = dict()
        while True:
            aum = self.Camino(s, t)
            if aum is None:
                break # ya no hay
            incr = min(aum.values(), key = (lambda k: k[1]))[1]
            u = t
            while u in aum:
                v = aum[u][0]
                actual = self.vecinos.get((v, u), 0) # cero si no hay
                inverso = self.vecinos.get((u, v), 0)
                self.vecinos[(v, u)] = actual + incr
                self.vecinos[(u, v)] = inverso - incr
                u = v
            maximo += incr
        return maximo

    def DibujarGrafo(self, titulo = "", eps = False):
        self.nombre = str(self.nombre)
        with open(self.nombre + ".gnu", "w") as f:
            if eps:
                print("set terminal postscript color enhanced", file = f) # http://www.gnuplotting.org/tag/epslatex/
                print("set output '" + self.nombre + ".eps'", file = f)
            else:
                print("set terminal png truecolor", file = f)
                print("set output '" + self.nombre + ".png'", file = f)
            print("set key off", file = f)
            print("set size square", file = f)
            print("unset colorbox", file = f)
            print("set title'" + titulo + "'", file = f)

            for n in self.nodos:
                temp = n.id
                n.id = str(n.id)
                if len(n.id) > 0:
                    n.id = str(n.id)
                    print("set label '" + str(n.id) + "' at " + str(n.posicion[0]) + "," + str(n.posicion[1]) + " left offset char -" + str(0.4 * len(n.id)) + ",0", file = f) # https://stackoverflow.com/questions/23690551/how-do-you-assign-a-label-when-using-set-object-circle-in-gnuplot
                print("set object circle at " + str(n.posicion[0]) + "," + str(n.posicion[1]) + " fillcolor rgb '" + n.color + "' fillstyle solid noborder size " + str(n.radio), file = f) # http://www.bersch.net/gnuplot-doc/layers.html

                n.id = temp # Corregida el cambio de nombre del identificador

            i = 1 # Deben ser mayores a 1
            for n in self.nodos:
                for v in self.vecinos[n]:
                    d = self.Distancia(n.posicion, v.posicion)

                    x1 = n.posicion[0]
                    y1 = n.posicion[1]

                    x2 = v.posicion[0]
                    y2 = v.posicion[1]

                    xNodo = n.radio * (x2 - x1) / d
                    yNodo = n.radio * (y2 - y1) / d

                    xVecino = n.radio * (x1 - x2) / d
                    yVecino = n.radio * (y1 - y2) / d

                    x1 = x1 + xNodo
                    x2 = x2 + xVecino
                    y1 = y1 + yNodo
                    y2 = y2 + yVecino

                    print("set arrow " + str(i) +
                        " from " + str(x1) + "," + str(y1) + " to " + str(x2) + "," + str(y2) + " linewidth " + str(self.pesos[(n, v)]), end = "", file = f) # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line
                    if self.dirigido:
                        print("", file = f)
                    else:
                        print(" nohead", file = f)
                    i = i + 1

            print("set style fill transparent solid 0.5 noborder", file = f)
            print("plot [-0.1:1.1][-0.1:1.1] NaN t''", file = f)
            #print("quit", file = f)

        system("gnuplot " + self.nombre +".gnu")
