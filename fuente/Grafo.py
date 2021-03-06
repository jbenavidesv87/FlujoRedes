from math import sqrt, cos, sin, pi, floor
from os import system, remove
class Grafo:

    def __init__(self):
        self.nombre = "grafo"
        self.dirigido = False
        self.nodos = [] # un conjunto
        self.pesos = dict() # un mapeo de pesos de aristas
        self.vecinos = dict() # un mapeo
        self.arcosColor = dict() # Hacer clase de Arco y agergar si son dirigidos a esto y no al grafo

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

    def ConectarNodos(self, n1, n2, peso = 1, c = (0, 0, 0)):
        color = "#"
        color += "00"
        color += format(c[0], '02x')
        color += format(c[1], '02x')
        color += format(c[2], '02x')
        if n1 not in self.nodos:
            self.AgregarNodo(n1)
        if n2 not in self.nodos:
            self.AgregarNodo(n2)
        self.vecinos[n1].add(n2)
        self.pesos[(n1, n2)] = peso
        self.arcosColor[(n1, n2)] = color
        if self.dirigido == False:
            self.vecinos[n2].add(n1) # Si no es dirigido, también debería haber una conexión bivalente
            self.pesos[(n2, n1)] = peso
            self.arcosColor[(n2, n1)] = color

    def EliminarNodo(self, n):
        temp = self.dirigido
        self.dirigido = False
        self.EliminarVecindades(n)
        self.dirigido = temp
        self.nodos.remove(n)

    def EliminarVecindades(self, n): # Eliminar también los colores de arco
        for v in self.vecinos[n]: # Por cada vecino de n
            del(self.pesos[(n, v)]) # Eliminar los pesos entre n y sus vecinos
            del(self.arcosColor[(n, v)])
        self.vecinos[n] = set() # Se eliminan los vecinos de n
        if not self.dirigido: # Si no es un grafo dirigido
            for k in list(self.vecinos): # Por cada k nodos que tengan vecindades
                if n in self.vecinos[k]: # Si n está en una de las vecindades de k
                    del(self.pesos[(k, n)]) # Se eliminan sus pesos
                    del(self.arcosColor[(k, n)])
                    self.vecinos[k].remove(n) # Y se remueve dicha vecindad con n

    def ModificarPesos(self, n, p):
        for v in self.vecinos[n]:
            self.pesos[(n, v)] = p
        if not self.dirigido: # Si no es un grafo dirigido
            for k in list(self.vecinos): # Por cada k nodos que tengan vecindades
                if n in self.vecinos[k]: # Si n está en una de las vecindades de k
                    self.pesos[(k, n)] = p

    def Distancia(self, p1, p2):
        d = sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return d

    def DistanciaTotal(self):
        d = 0.0
        for n in self.vecinos:
            for v in self.vecinos[n]:
                d += self.Distancia(n.posicion, v.posicion)
        return d

    def DistanciaPromedio(self):
        d = 0
        noCero = 0
        for (k, val) in self.Floyd_Warshall().items(): # De todos los caminos más cortos entre todos los pares de vértices
            d = d + val
            if val != 0:
                noCero = noCero + 1
        d = d / noCero
        return d

    def DensidadPromedio(self): # ClusterCoeficient
        if self.dirigido:
            print("Error, la densidad promedio se debe medir en un grafo no dirigido")
            return -1
        else:
            coeficienteCluster = 0
            for nodo in self.nodos:
                n = len(self.vecinos[nodo])
                if n > 1:
                    m = 0 # Arcos con vecinos
                    for v1 in self.vecinos[nodo]:
                        for v2 in self.vecinos[nodo]:
                            if v2 in self.vecinos[v1]:
                                m = m + 1
                    coeficienteCluster += m / (n * (n - 1)) # la m está ya por 2
            return coeficienteCluster / len(self.nodos)


    def Floyd_Warshall(self): # Camino más corto entre todos los pares de vértices
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

    def CaminoAumentante(self, s, t, f): # construcción de un camino aumentante
        # s : origen
        # t : destino
        cola = [s] # Se almacena el nodo inicial
        usados = set()
        camino = dict()
        while len(cola) > 0: # Mientras haya nodos por recorrer
            u = cola.pop(0) # Se obtiene el nodo por recorrer y se almacena como el nodo u (actual)
            usados.add(u) # Se agrega a usados (evita que se recorra en dos sentidos si fuera dirigido)
            for (w, v) in self.pesos: # Cada peso de cada arista
                if w == u and v not in cola and v not in usados: # Del nodo actual, si su vecino no está en la cola ni ha sido recorrido (usado) ; ¿se pueden poner sólo los vecinos de u?;  ¿se puede quitar v not in cola?
                    pesoActual = f.get((u, v), 0) # Del flujo (grafo reducido) se obtiene el peso que hay entre el nodo actual y su vecino
                    dif = self.pesos[(u, v)] - pesoActual # Diferencia entre el peso del arco en el Grafo y del peso en el arco en el grafo reducido
                    if dif > 0: # Si se permite el paso del flujo
                        cola.append(v) # Se agrega el vecino a la cola (se vuelve el siguiente nodo a recorrer)
                        camino[v] = (u, dif) # Se agrega como camino que llega a v del nodo u (actual, la diferencia de pesos del Grafo al Grafo reducido)
        # Si no se permite el paso del flujo a otro nodo
        if t in usados: # Y si se ha llegado al final del camino de s (nodo inicial) a t (nodo final)
            return camino # Se regresa ese camino
        else: # Si no se alcanzó dicho nodo
            return None # No se regresa nada

    def Ford_Fulkerson(self, s, t): # Máximo flujo entre un vértice inicial (s) y uno final (t)
        if s == t: # Si el nodo inicial es el nodo destino
            return 0 # el peso máximo es 0
        maximo = 0
        flujo = dict()
        while True:
            aum = self.CaminoAumentante(s, t, flujo) # Regresa todos los caminos que van de s a t
            if aum is None: # Si no regresa nada
                break # Ya no hay caminos y se acaba el ciclo
            incr = min(aum.values(), key = (lambda k: k[1]))[1] # De todos los pesos en todos los caminos de s a t, se elige el menor
            u = t
            while u in aum:
                v = aum[u][0]
                actual = flujo.get((v, u), 0) # cero si no hay
                inverso = flujo.get((u, v), 0)
                flujo[(v, u)] = actual + incr
                flujo[(u, v)] = inverso - incr
                u = v
            maximo += incr
        return maximo

    def Anchura(self, s, i, debug = False):
        while len(s) > 0:
            n = s.pop()
            n.Color(255, 0, 0)
            if debug:
                self.nombre = "{:06d}".format(i)
                self.DibujarGrafo(titulo = str(i))
                remove('{:06d}.gnu'.format(i)) # https://pyformat.info/
            i = i + 1
            for v in self.vecinos[n]:
                if v.color != "#00ff0000":
                    s.insert(0, v)
            if debug:
                self.Anchura(s, i, True)
            else:
                self.Anchura(s, i)
        return i

    def Profundidad(self, s, i, debug = False):
        s.Color(255, 0, 0)
        if debug:
            self.nombre = "{:06d}".format(i)
            self.DibujarGrafo(titulo = str(i))
            remove('{:06d}.gnu'.format(i)) # https://pyformat.info/
        i = i + 1
        for v in self.vecinos[s]:
            if v.color != "#00ff0000":
                if debug:
                    i = self.Profundidad(v, i, True)
                else:
                    self.Profundidad(v, i)
        return i

    # Toma los nodos a ser dispuestos de manera circular; y el radio y el centro de la cirfunferencia a la que se adscribirán
    def Circular(self, nodos, radio = 0.5, centro = (0.5, 0.5)):
        N = len(nodos)
        r = radio # Radio de la circunferencia
        P = 2 * pi * r # Perímetro de la circunferencia
        if N > 15:
            rNodo = P / N / 3 # Radio para cada nodo
        else:
            rNodo = P / 15 / 3 # Radio para cada nodo
        theta = 2 * pi / N # Fracción angular que ocupará cada nodo
        for i in range(N):
            n = nodos[i]
            n.radio = rNodo
            n.posicion = (
                centro[0] + r * cos(theta * i), centro[1] + r * sin(theta * i)
            )

    def Cuadrado(self, nodos):
        N = len(nodos) # Total de nodos
        lado = floor(sqrt(N))
        for i in range(N):
            n = nodos[i]
            n.radio = 1 / N
            n.posicion = ((i % lado) / (lado - 1), 1 - int(i / lado) / (lado - 1)) # la parte de la y tiene 1 - para que empiece desde arriba y no desde abajo

    def PasoManhattan(self, n, v, paso, nuevasVecindades = None): # self es grafo, n es el nodo papá, v es el que está entrando
    # Cambiar esto para que sólo haga falta pasar el grafo y que se devuelva el grafo conectado con Manhattan completo :D :D :D
        if self.dirigido:
            for v1 in self.vecinos[v]:
                self.ConectarNodos(n, v1)
                if paso > 1:
                    self.PasoManhattan(n, v1, paso - 1)
        else:
            for v1 in self.vecinos[v]:
                if n != v1:
                    nuevasVecindades.append((n, v1))
                if paso > 1:
                    self.PasoManhattan(n, v1, paso - 1, nuevasVecindades)
            return nuevasVecindades

    def DibujarGrafo(self, titulo = "", eps = False, mostrarPesos = False):
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
                    print("set label '" + str(n.id) + "' at " + str(n.posicion[0]) + "," + str(n.posicion[1]) + " left offset char -" + str(0.4 * len(n.id)) + ",0 front", file = f) # https://stackoverflow.com/questions/23690551/how-do-you-assign-a-label-when-using-set-object-circle-in-gnuplot
                print("set object circle at " + str(n.posicion[0]) + "," + str(n.posicion[1]) + " fillcolor rgb '" + n.color + "' fillstyle solid noborder front size " + str(n.radio), file = f) # http://www.bersch.net/gnuplot-doc/layers.html

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
                        " from " + str(x1) + "," + str(y1) + " to " + str(x2) + "," + str(y2) + " linewidth " + str(self.pesos[(n, v)]) + "lc rgb '" + self.arcosColor[(n, v)] + "' back", end = "", file = f) # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line

                    if n not in self.vecinos[v]:
                        print("", file = f)
                    else:
                        print(" nohead", file = f)

                    if mostrarPesos:
                        pmX = (x1 + x2) / 2
                        pmY = (y1 + y2) / 2
                        deltaX = x1 - x2
                        m = 0
                        if deltaX == 0:
                            m = 1000
                        else:
                            m = (y1 - y2) / deltaX
                        xLabel = 0
                        yLabel = 0
                        if m == 0:
                            yLabel = 0.03
                        elif m == 1000:
                            xLabel = -0.03
                        elif m > 0:
                            xLabel = -0.07
                            yLabel = -0.03
                        elif m < 0:
                            xLabel = 0.07
                            yLabel = -0.03
                        print("set label '" + str(self.pesos[(n, v)]) + "' at " + str(pmX + xLabel) + "," + str(pmY + yLabel) + " left offset char -" + str(0.4 * len(str(self.pesos[(n, v)]))) + ",0", file = f)

                    i = i + 1

            print("set style fill transparent solid 0.5 noborder", file = f)
            print("plot [-0.1:1.1][-0.1:1.1] NaN t''", file = f)
            #print("quit", file = f)

        system("gnuplot " + self.nombre +".gnu")
        remove('{}.gnu'.format(self.nombre))
