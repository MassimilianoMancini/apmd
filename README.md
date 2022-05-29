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
- G: Grafo principale
- A: Grafo degli attori di cui al punto 5. A ogni nuovo inserimento creo tanti edge tra l'attore e gli attori del film
- P: Grafo della produttività dove si hanno i seguenti nodi: anno che ha come attributo l'attore più prolifico e un arco pesato verso i nodi di tipo attore. Il peso indica il numero di film fatti dall'attore fino alla decade di cui al nodo anno. In fase di lettura del file, per ogni attore si crea o incrementa di uno il peso dell'arco. All'inizio l'anno avrà come attore più prolifico il primo con un arco di peso 1. Ogni volta che viene aggiunto un arco nel grafo principale si utilizza l'informazione sull'anno per aggiungere un nuovo arco oppure incrementare il peso di un arco. Se si procede con un incremento allora si verifica se il valore del nodo anno è minore di quello dell'arco appena aggiornato e se sì, si procede aggiornando gli attributi del nodo anno (n. film e attore). (funzione decade(year))
Il ricorso al grafo al posto di altre strutture dati, è giustificato dalla funzione hash che evita il ricorso a dizionari di trascodifica (attore - intero).

### Ciclo principale di caricamento dati
Il ciclo principale carica di dati dal file di testo nelle strutture dati preposte. Di seguito una descrizione delle azioni

- Legge riga
    - estrae attore, film, anno
    - se incontra problemi (anno non presente, oppure arco già presente), genera apposito file di log 
    - crea un nuovo arco nel grafo principale G
    - crea un nuovo arco nel grafo produttività P

### Question 1
Generare le sommatorie in fase di caricmento costa troppo tempo. Decido di suddividere i tempi in due: tengo basso il caricamento mettendo per ogni nodo solo la decade in corso e non le precedenti
In fase di richiamo della funzione, dovrò ciclare su tutti i nodi decade dall'inizio fino a untilDecade. Per ogni attore mi tengo un dizionario con nome attore e 
Accedo al nodo decade e restituisco il nome dell'attore (attributo del nodo).

### Question 2
per la domanda 2, bisogna prima trovare la più grande componente connessa. Per la centralità fare k=log(n) BFS

### Question 3
```
max = 1
for film1 in films if film1.degree > max

    if max = 1 then max = 2
    for actor in film1.actors if actor.degree > max
        visited = null
        for film2 in actor.films if not in visited and film2.degree > max
            n = intersect(set(film1), set(film2))
            if n > max
                max = n
                filmI = film1
                filmII = film2
        visited = visited + film2

```