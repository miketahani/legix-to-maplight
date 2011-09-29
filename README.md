# legix to maplight

names organizations that influenced the creation of california state codes.

### technical description

a mashup script that combines [legix](http://legix.info)'s API and [maplight](http://maplight.org)'s API.

1. get legix-formatted file as command-line input *(e.g., division one of the business professional code at <http://legix.info/us-ca/code-bpc/doc(div1).json>)*
2. parse that json file for statute information
3. look up corresponding bill number
4. use bill number to search [maplight](http://maplight.org)'s california API
5. list organizations and their position (support/oppose) on the legislation

### future

* link campaign contribution data
* building a frontend for one-click, on-demand information retrieval
* data visualization (think graphs, as in graph theory)

### author

mike tahani