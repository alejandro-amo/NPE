<div style="text-align: center" align="center">
    <h1>Open Data Source for 🚽 NPE App 🚽 </h1>
    <p>
        <strong>As part of the deep revamping of NPE App, its data backends and standards,<br/>
we publish this open repository which is intended to contain a GEOJSON file <br/>
            with the latest establishment information available in the App.<br/>
The data file is built directly from the original database of supporting establishments<br/>
          and is part of ACCU Catalunya's pilot project to move to Open Data standards.
</strong>
    </p>
    <br>
    <img src=https://github.com/ACCU-Catalunya/nopucesperar-geojson/assets/1114811/a98dcf7a-8c6f-44f9-a5d0-eefc957c70e5">
    <br>
    <p style="text-align: center">
        <a href="#what-is-npe">What is NPE?</a> •
        <a href="#geojson-file-syntax">GeoJSON file syntax</a> •
        <a href="#license">License</a> •
        <a href="#questions-similar-challenges">Questions? Similar challenges?</a>
    </p>
    <br>
    <p>
        <em>NOTE: This dataset is published under ODC's Open DataBase License 1.0. You are free to (re)use the data for societal and scientific projects, for learning about software development, about interoperability standards and data formats like GeoJSON, etc. but please, take some time to take a look at the copy of the license that is included in this repository. If this repository is useful for you in a way or another, please give it a star ⭐️  and send me an email to tell your story :)</em>
    </p>
    <br>
    <p style="text-align: center">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/ACCU-Catalunya/nopucesperar-geojson">
        <img alt="license" src="https://img.shields.io/badge/License-ODbL%201.0-blue"> 
    </p>
</div>


## What is NPE? 

NoPucEsperar (I Can't Wait, "NPE" for short) is an initiative developed by the Association of Crohn's Disease and Ulcerative Colitis Patients of Catalonia (ACCU Catalonia) and the Inflammatory Bowel Disease (IBD) Unit of the University Hospital of Girona. It aims to assist individuals with inflammatory bowel diseases and other medical conditions that require urgent restroom access.

The project provides NPE cards to eligible patients, allowing them to quickly and freely access restrooms in various locations (mostly commercial establishments that join the project to support the patients). 
The initiative seeks to improve the quality of life for patients by offering convenient restroom access and raising awareness about inflammatory bowel diseases.

## GeoJSON file syntax

The file provides the data source for a new, pilot version of NPE App that is currently being developed. It's a regular GeoJSON format file, starting at the first level with the typical "FeatureCollection" and having the following structure:

```{"type": "FeatureCollection", "features": [ {establishment}, {establishment}, {establishment}, {...}]}```

Then, at the second level, each establishment object has the following structure (please note the longitude, latitude order that the GeoJSON standard implements!):

```{"type": "Feature", "geometry": {"type": "Point", "coordinates": [longitude, latitude]}, "properties": {"key": "value", "key2": "value2"}}```

And finally, at the third level is where the GeoJSON standard provides room for free definition of infinite key:value pairs that we may need. In our case we provide the following values:

- ```nombre```: Name of the establishment supporting NPE!
- ```direccion```: Address of the stablishment (the result of concatenating the typical "address1" and "address2" components into a single string)
- ```poblacion```: City/town of the establishment
- ```telefono```: Phone number. It can contain two phone numbers separated by ```/```, exit codes ```+``` for some phone numbers in Andorra, and extension information between parenthesis i.e: ```(ext. 123)```
- ```codigopostal```: Postal code. Since this project is focused in the spanish community of Catalonia, the lenght of the postal codes is 5 chars, typically 5 numbers, but it's treated as text in order to allow postal codes from Andorra i.e: ```AD123``` too.

> NOTE: `googlemaps` was planned but we need to remove it for compliance reasons: Google kindly asks us to implement this query in realtime at client level and NOT storing data from its API). The original description was:
> 
> ```googlemaps```: An URL pointing to the establishment sheet reported by Google Maps, if any. Null if Google reported no matches for the stablishment. Google does not fail 99% of time. However, the accuracy of Google's bet on this data may vary depending on several factors that are not under our control. Always be prepared for some minor glitches here. You can always report errors to us so we update the database. 

## License

This dataset is published under ODC's Open DataBase License 1.0. Please, take some time to take a look at the copy of the license that is included in this repository.

## Questions? Similar challenges?

📧 Drop me an email then: [hello@alejandroamo.eu](mailto:hello@alejandroamo.eu)
