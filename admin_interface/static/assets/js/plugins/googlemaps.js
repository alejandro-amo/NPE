// noinspection JSUnresolvedReference,JSUnusedGlobalSymbols

let map;
let marker;
let markers = [];

let latitudElement = document.getElementById('id_latitud');
let longitudElement = document.getElementById('id_longitud');

let latitud = latitudElement ? parseFloat(latitudElement.value) : 0.0;
let longitud = longitudElement ? parseFloat(longitudElement.value) : 0.0;

const mapOptions = {
  mapId: 'ae555d8787365c53',
  center: {lat: 41.65, lng: 1.7},
  zoom: 7,
  disableDefaultUI: true,
  zoomControl: true,
  mapTypeControl: false,
  scaleControl: false,
  streetViewControl: false,
  rotateControl: false,
  fullscreenControl: false,
  scrollwheel: false,
};

function setDetailMarker(lat, long) {
  if (marker === null || marker === undefined) {
    // No existe un marcador llamado "marker" en el mapa
    marker = new google.maps.Marker({
      position: {lat: lat, lng: long},
      map: map
    });
  } else {
    // Ya existe un marcador llamado "marker" en el mapa
    marker.setPosition(new google.maps.LatLng(lat, long));
  }
}

function setIndexMarker(lat, long, name, markerId) {
    let indexMarker;
    console.log('Receiving coords in setIndexMarker: ' + parseFloat(lat) + ', ' + long.toString())
    indexMarker = new google.maps.Marker({
        position: {lat: parseFloat(lat), lng: parseFloat(long)},
        title: name.toString(),
        name: 'marker_' + markerId.toString(),
        url: '/establiments/detall/?id=' + markerId.toString(),
        map: map
    });

    google.maps.event.addListener(indexMarker, 'click', function() {
        console.log('redirecting to ' + indexMarker.url)
      window.location.href = indexMarker.url;
    });

    return indexMarker;
}

// noinspection JSUnusedGlobalSymbols
function initDetailMap() {
  map = new google.maps.Map(document.getElementById('map'), mapOptions);
  if (latitud != 0 && longitud != 0 ) {
      setDetailMarker(latitud, longitud);
    }

}


function initIndexMap() {
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    markers = populateIndexMarkers();
    let algorithm = new markerClusterer.SuperClusterAlgorithm({ maxZoom: 12, radius: 100});
    let config = { map, markers, algorithm };
    new markerClusterer.MarkerClusterer(config);
}



async function processGeocodeResponse() {
    try {
        const response = await queryGeoCodeAPI();
        console.log('processGeocodeResponse is getting:', response);

        let status = response.status;
        let lat = response.results[0].geometry.location.lat.toFixed(6);
        let lng = response.results[0].geometry.location.lng.toFixed(6);
        let formattedAddress = response.results[0].formatted_address;
        // var streetNumber, route, locality, postalCode;

        /*
        var addressComponents = response.results[0].address_components;
        for (var i = 0; i < addressComponents.length; i++) {
            var component = addressComponents[i];
            var types = component.types;

            if (types.includes('street_number')) {
                streetNumber = component.long_name;
            } else if (types.includes('route')) {
                route = component.long_name;
            } else if (types.includes('locality')) {
                locality = component.long_name;
            } else if (types.includes('postal_code')) {
                postalCode = component.long_name;
            }

        }
        */

        console.log('Status:', status);
        console.log('Latitud:', lat);
        console.log('Longitud:', lng);
        console.log('Dirección formateada:', formattedAddress);
        /*
        console.log('Número de calle:', streetNumber);
        console.log('Nombre de calle:', route);
        console.log('Localidad:', locality);
        console.log('Código postal:', postalCode);

         */

        // show results in DOM
        document.getElementById('googleresponse').style.display = "";
        document.getElementById('googleresponse-fulladdress').innerHTML = formattedAddress;
        document.getElementById('googleresponse-gpscoords').innerHTML = lat + ',&nbsp;' + lng;
        let copygpscoords;
        copygpscoords = document.getElementById('copygpscoords');
        copygpscoords.addEventListener('click', function() {
            document.getElementById('id_latitud').value = lat;
            document.getElementById('id_longitud').value = lng;
        })

    } catch (error) {
        console.log('Error:', error);
    }
}



async function queryGeoCodeAPI() {
    // var nombre = document.getElementById('id_nombre').value;
    let direccion = document.getElementById('id_direccion').value;
    let codigoPostal = document.getElementById('id_codigo_postal').value;
    let poblacion = document.getElementById('id_poblacion').value;

    let googlequery = '';

    if (direccion) {
        googlequery += direccion;
    }

    if (codigoPostal) {
        googlequery += ', ' + codigoPostal;
    }

    if (poblacion) {
        googlequery += ', ' + poblacion;
    }

    googlequery = encodeURIComponent(googlequery);

    let url = '/googlemapsproxy/geocode/json?language=ca&bounds=rectangle:40.522,0.158|42.868,3.327&components=country:ES&address=' + googlequery;


    return fetch(url, {
        method: 'GET'
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            console.log('queryGeoCodeAPI is getting:', data); // Imprimir la respuesta recibida en la consola
            return data;
            // Puedes realizar más acciones con los datos de la respuesta aquí
        })
        .catch(function (error) {
            console.log('queryGeoCodeAPI error:', error);
            alert("S'ha produït un error consultant Google Geocoding: " + error);
        });
}

// noinspection EqualityComparisonWithCoercionJS
async function processPlacesResponse() {
    let stage2response = '';
    try {
        const stage1response = await queryPlacesAPI();
        console.log('processPlacesResponse is getting:', stage1response);

        // noinspection EqualityComparisonWithCoercionJS
        let place_id;
        if (stage1response.status == 'OK') {
            place_id = stage1response.candidates[0].place_id
            console.log('Places stage 1 completed. Proceeding to stage 2 with place_id: ' + place_id)
            stage2response = await queryPlacesAPI2(place_id);

        } else { // noinspection EqualityComparisonWithCoercionJS
            if (stage1response.status == 'ZERO_RESULTS') {
                        console.log('Google query status ZERO_RESULTS')
                        return null
                    } else {
                        console.log('Google query status' + stage1response.status)
                        alert('Error fent petició a Google Places (fase 2):' + stage1response.status)
                        return null
                    }
        }

        // process the response from the second request to google places API (defails by place id)
        if (stage2response === null) {
            return null
        }
        let query_status = stage2response.status;
        let place_name = stage2response.result.name;
        let place_status = stage2response.result.business_status;
        let change_badge_color;
        if (place_status === 'OPERATIONAL') {
            place_status = 'Operatiu';
        } else if (place_status === 'CLOSED_PERMANENTLY') {
            place_status = 'TANCAT DEFINITIVAMENT';
            change_badge_color = document.getElementById('googleresponse-place-status').parentNode;
            change_badge_color.classList.replace('bg-info', 'bg-danger');
        } else if (place_status === 'CLOSED_TEMPORARILY') {
            place_status = 'TANCAT TEMPORALMENT';
            change_badge_color = document.getElementById('googleresponse-place-status').parentNode;
            change_badge_color.classList.replace('bg-info', 'bg-warning');
        } else if (typeof place_status === 'undefined') {
            place_status = '(no s\'ha reportat cap esatabliment coincident)'
        }
        let place_schedule = stage2response.result.weekday_text;
        if (typeof place_schedule === 'undefined') {
            place_schedule = '(no informats)';
        }
        let place_telf = stage2response.result.formatted_phone_number;
        if (typeof place_telf === 'undefined') {
            place_telf = '(no informat)';
        } else {
            place_telf = place_telf.replace(/\s/g, "");
        }
        let place_web = stage2response.result.website;
        if (typeof place_web === 'undefined') {
            place_web = '(no informada)';
        }


        console.log('Status petición:', query_status);
        console.log('Nombre:', place_name);
        console.log('Status establecimiento:', place_status);
        console.log('Horarios:', place_schedule);
        console.log('Teléfono:', place_telf);
        console.log('Web:', place_web);

        // show results in DOM
        document.getElementById('googleresponse').style.display = "";
        document.getElementById('googleresponse-place-name').innerHTML = place_name;
        document.getElementById('googleresponse-place-status').innerHTML = place_status;
        document.getElementById('googleresponse-place-schedule').innerHTML = place_schedule;
        document.getElementById('googleresponse-place-telf').innerHTML = place_telf;
        document.getElementById('googleresponse-place-web').innerHTML = place_web;

    } catch (error) {
        console.log('Error:', error);
    }
}

async function queryPlacesAPI() {
    let nombre = document.getElementById('id_nombre').value;
    let direccion = document.getElementById('id_direccion').value;
    let codigoPostal = document.getElementById('id_codigo_postal').value;
    let poblacion = document.getElementById('id_poblacion').value;

    let googlequery = nombre;

    if (direccion) {
        googlequery += ', ' + direccion;
    }

    if (codigoPostal) {
        googlequery += ', ' + codigoPostal;
    }

    if (poblacion) {
        googlequery += ', ' + poblacion;
    }

    googlequery = encodeURIComponent(googlequery);

    let url = '/googlemapsproxy/place/findplacefromtext/json?inputtype=textquery&locationbias=rectangle:40.522,0.158|42.868,3.327&input=' + googlequery;

    return fetch(url, {
        method: 'GET'
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            console.log('queryPlacesAPI - stage 1 - is getting:', data); // Imprimir la respuesta recibida en la consola
            return data
        })
        .catch(function (error) {
            console.log('queryPlacesAPI error:', error);
            alert("S'ha produït un error consultant l'identificador d'establiment a Google Places: " + error);
        });
}

async function queryPlacesAPI2(place_id) {

    let url = '/googlemapsproxy/place/details/json?place_id=' + place_id;

    return fetch(url, {
        method: 'GET'
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            console.log('queryPlacesAPI - stage 2 - is getting:', data); // Imprimir la respuesta recibida en la consola
            return data
        })
        .catch(function (error) {
            console.log('queryPlacesAPI - stage 2- error:', error);
            alert("S'ha produït un error consultant els detalls de l'establiment a Google Places: " + error);
        });
}
