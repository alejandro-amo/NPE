# NPE
NoPucEsperar Admin. Data administration dashboard, API and backend for NoPucEsperar App.

## Features
### General dashboard with data quality controls and map overview  

![image](https://github.com/alejandro-amo/NPE/assets/1114811/05b97d1c-cb2f-4736-94aa-ef0995f526af)

### Custom listings for several criteria: text search, establishment type search, active/inactive search

![image](https://github.com/alejandro-amo/NPE/assets/1114811/9b2c95fb-6def-476f-b19d-bd73d2a161ff)

### Real time data from Google: operational status of the stablishment, detailed address, time schedule, etc:

![image](https://github.com/alejandro-amo/NPE/assets/1114811/7ffe2aa2-a9d3-4a46-a21e-ced46ba8c329)

### RESTful API for interoperability with other management tools or integration with other applications in the future
Implemented in Django REST Framework. See [api_rest.md](https://github.com/alejandro-amo/NPE/blob/master/api_rest.md) for details (documented in spanish)

### Open licensed, standards based file exported every time that a change is made.
Establishments database is constantly exported to a GeoJSON file in an independent repository. The establishments database is licensed under Open License Data Base and it can be reused for any educative or social benefit purposes. Latest version of the GeoJSON file can be obtained by cloning the following repo: https://github.com/ACCU-Catalunya/nopucesperar-geojson   

