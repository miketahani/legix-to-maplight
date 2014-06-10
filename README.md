#### This project is unsupported and the APIs may have changed since it was last updated 

# Legix to Maplight

Expose organizations that influenced the creation of california state codes.

### Requirements

The only third-party requirement is JSONPath (`easy_install jsonpath` on Windows).

### Technical Description

A mashup script that combines [Legix](http://legix.info)'s API and [Maplight](http://maplight.org)'s API.

1. Get legix-formatted file as command-line input *(e.g., Division 1 of the Business Professional Code at <http://legix.info/us-ca/code-bpc/doc(div1).json>)*
2. Parse that JSON file for statute information
3. Look up corresponding bill number in **/data/statuteslist.json**
4. Use the returned bill number to search [Maplight](http://maplight.org)'s California API
5. List organizations and their position (support/oppose) on the legislation

### Future

* Link this data to campaign contribution data
* Build a frontend for one-click, on-demand information retrieval
* Data visualization (think graphs, as in graph theory)

### Author Info

Mike Tahani, m.tahani at gmail
