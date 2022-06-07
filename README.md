# IMDB Actor database
Il presente progetto viene realizzato nell'ambito del corso di 
Laurea Magistrale dell'Università di Firenze. 
## APAD
Nel progetto di Algoritmi e Programmazione per l'Analisi dei Dati viene richiesto di utilizzare un file di testo come sorgente di dati al fine di realizzare una o più strutture dati, tra cui ricoprono particolare rilevanza i grafi, su cui dovranno essere eseguite misure che realizzano quanto studiato teoricamente durante il corso.

## Il progetto
Riporto qui i punti più importanti che intendo realizzare e seguire la conduzione del progetto:
1. Viene dapprima eseguita una fase di caricamento dei dati. In questa fase viene letto il file di testo e vengono create tutte le strutture dati necessarie a soddisfare le richieste di progetto. In questa fase si effettua anche una pulizia e bonifica dei dati sporchi o ridondanti.
2. Le richieste di progetto sono le seguenti:
   1. Creare un grafo tramite NetworkX
   2. Rispondere alla richiesta di quale sia l'attore più prolifico fino all'anno x, con x in 1930..2020 (step 10)
   3. Approssimare la closeness centrality e dire quali siano i 10 attori più centrali
   4. Quali sono i due film che condividono il maggior numero di attori
   5. Costruire il grafo degli attori dove l'arco viene tracciato se due attori hanno recitato insieme nello stesso film e dire quali siano gli attori che hanno collaborato di più
   
## Strutture dati
- mainGraph: Grafo principale
- actorGraph: Grafo degli attori di cui al punto 5. Creato a partire da G
- prodGraph: Grafo della produttività dove si hanno i seguenti nodi: anno che ha come attributo l'attore più prolifico e un arco pesato verso i nodi di tipo attore. Il peso indica il numero di film fatti dall'attore fino alla decade di cui al nodo anno. In fase di lettura del file, per ogni attore si crea o incrementa di uno il peso dell'arco. All'inizio l'anno avrà come attore più prolifico il primo con un arco di peso 1. Ogni volta che viene aggiunto un arco nel grafo principale si utilizza l'informazione sull'anno per aggiungere un nuovo arco oppure incrementare il peso di un arco. Se si procede con un incremento allora si verifica se il valore del nodo anno è minore di quello dell'arco appena aggiornato e se sì, si procede aggiornando gli attributi del nodo anno (n. film e attore). (funzione decade(year))
Il ricorso al grafo al posto di altre strutture dati, è giustificato dalla funzione hash che evita il ricorso a dizionari di trascodifica (attore - intero).

### Ciclo principale di caricamento dati
Il ciclo principale carica di dati dal file di testo nelle strutture dati preposte. Di seguito una descrizione delle azioni

- Legge riga
    - estrae attore, film, anno
    - se incontra problemi (anno non presente, oppure arco già presente), genera apposito file di log 
    - crea un nuovo arco nel grafo principale 
    - crea un nuovo arco nel grafo produttività 

### Question 1
In fase di richiamo della funzione, dovrò ciclare su tutti i nodi decade dalla decade data in input fino all'ultima decade. 
Accedo al nodo decade e restituisco il nome dell'attore (attributo del nodo) con l'arco di peso maggiore.

### Question 2
#### Trovare la più grande componente connessa
Eseguire l'algoritmo con BFS filtrata anche per anno
#### Approssimare la centralità di tutti i nodi
Eseguire k BFS e accumulare in apposito attributo di nodo la distanza totale. Poi scorrere tutti i nodi e calcolare la closeness centrality approssimata. Utilizzare una struttura heap per mantenere i top ten actors


### Question 3
Si fa l'intersezione tra tutti i film a distanza 2 con tre livelli di ciclo: movie1, actor, movie2. Si salta movie1 e movie2 quando la loro cardinalità è minore di quella incontrata, si salta actor se cardinalità minore di 2

### Question 4
Si cicla su tutti i film con cardinalità almeno 2. Per ogni film si creano combinations di archi tra tutti gli attori. Nel caso di arco già presente, se ne aumenta il peso