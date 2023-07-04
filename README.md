# NPE
NoPucEsperar Admin. Data administration dashboard, API and backend for NoPucEsperar App.

## Features
### General dashboard with data quality controls and map overview  

![Captura de pantalla 2023-06-08 020021](https://github.com/alejandro-amo/NPE/assets/1114811/c83305a7-c7b1-4449-8cc1-b8a6a78ef31a)

### Custom listings for several criteria: text search, establishment type search, active/inactive search

![cerca-3](https://github.com/alejandro-amo/NPE/assets/1114811/c49c66d1-334e-452b-93e4-9390196f8fae)

### Real time data from Google: operational status of the stablishment, detailed address, time schedule, etc:

![Captura de pantalla 2023-06-08 020518](https://github.com/alejandro-amo/NPE/assets/1114811/5ab18a2e-6cfa-411f-a680-4082eeff2058)

### RESTful API for interoperability with other management tools or integration with other applications in the future
Implemented in Django REST Framework. See [api_rest.md](https://github.com/alejandro-amo/NPE/blob/master/api_rest.md) for details (documented in spanish)

### Open licensed, standards based file exported every time that a change is made.
Establishments database is constantly exported to a GeoJSON file in an independent repository. The establishments database is licensed under Open License Data Base and it can be reused for any educative or social benefit purposes. Latest version of the GeoJSON file can be obtained by cloning the following repo: https://github.com/ACCU-Catalunya/nopucesperar-geojson   

