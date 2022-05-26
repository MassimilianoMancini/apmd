# IMDB Actor database
Il presente progetto viene realizzato nell'ambito del corso di 
Laurea Magistrale dell'Università di Firenze. 
## APAD
Nel progetto di Algoritmi e Programmazione per l'Analisi dei Dati viene richiesto di utilizzare un file di testo come sorgente di dati al fine di realizzare una o più strutture dati, tra cui ricoprono particolare rilevanza i grafi, su cui dovranno essere eseguite misure che realizzano quanto studiato teoricamente durante il corso.

## Il progetto
Riporto qui i punti più importanti che intendo realizzare e seguire la conduzione del progetto:
1. Viene dapprima eseguita una fase di caricamento dei dati. In questa fase viene letto il file di testo e vengono create tutte le strutture dati necessarie a soddisfare le [richieste][1] di progetto. In questa fase si effettua anche una pulizia e bonifica dei dati sporchi o ridondanti.
2. [1] Le richieste di progetto sono le seguenti:
   1. Creare un grafo tramite NetworkX
   2. Rispondere alla richiesta di quale sia l'attore più prolifico fino all'anno x, con x in 1930..2020 (step 10)
   3. Approssimare la closeness centrality e dire quali siano i 10 attori più centrali
   4. Quali sono i due film che condividono il maggior numero di attori
   5. Costruire il grafo degli attori dove l'arco viene tracciato se due attori hanno recitato insieme nello stesso film e dire quali siano gli attori che hanno collaborato di più
   
## Strutture dati
G: Grafo principale
A: Grafo degli attori di cui al punto 5
P: Grafo della produttività dove si hanno i seguenti nodi: anno che ha come attributo l'attore più prolifico e un arco pesato verso i nodi di tipo attore. Il peso indica il numero di film fatti dall'attore fino all'anno di cui al nodo anno. In fase di lettura del file, per ogni attore si crea o incrementa di uno il peso dell'arco. All'inizio l'anno avrà come attore più prolifico il primo con un arco di peso 1. Ogni volta che viene aggiunto un arco nel grafo principale si utilizza l'informazione sull'anno per aggiungere un nuovo arco oppure incrementare il peso di un arco. Se si procede con un incremento allora si verifica se il valore del nodo anno è minore di quello dell'arco appena aggiornato e se sì, si procede aggiornando gli attributi del nodo anno (n. film e attore).
Il ricorso al grafo al posto di altre strutture dati, è giustificato dalla funzione hash che evita il ricorso a dizionari di trascodifica (attore - intero).

### Question 2
per la domanda 2, bisogna prima trovare la più grande componente connessa. Per la centralità fare k=log(n) BFS

### Question 3
```
max = 1
if film1.degree > max
    if max = 1 then max = 2

    if actor.degree > max
        film2 = actor.adj[1]
        if film2.degree > max
            n = set(film1) inersect set(film2)
            if n > max
                max = n
                filmI = film1
                filmII = film2

```

Per la domanda


