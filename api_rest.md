# Rutas de la API de administración de NPE
(todos los objetos se devuelven en formato JSON)

## /admin/api/establecimientos/ (GET)
Parámetros que acepta:
- Sin parámetros, obtiene la lista de establecimientos completa, ordenada por ID descendiente (los mas recientes primero). 
- `buscar`: obtiene la lista de establecimientos que tengan coincidencia con el texto buscado. Busca en nombre de establecimiento, dirección, código postal y población. La búsqueda no es sensible a mayúsculas ni a acentos. Se pueden incluir espacios en los términos de búsqueda mediante el método habitual de urlencode (`%20`)
- `ordenar_por`: este parámetro hace lo que su nombre indica, aceptando las siguientes columnas: `id`, `nombre`, `direccion`, `poblacion`, `codigo_postal`, `fecha_creacion`,`fecha_actualizacion`.
- `orden_inverso`: Si se especifica este parámetro con un valor de 1, los resultados se presentarán en orden inverso (de la Z a la A, del 9 al 0).
- `incluir_inactivos`: Si se especifica este parámetro con un valor de 1, los resultados incluyen establecimientos marcados como inactivos.
- `pagina`: nos permite elegir la página de resultados que queremos recibir.
- `porpag` nos permite alterar la cantidad de resultados por página, que por defecto es 100. No acepta valores mayores y no se recomienda cambiar este ajuste.

> NOTA: la búsqueda limitada a un solo campo (por ejemplo, buscar solamente por nombre) no está implementada. Sin embargo, con búsquedas suficientemente específicas se pueden obtener resultados equivalentes.
> Por ejemplo, si buscamos `hospitalet de llobregat`, es poco probable que en los resultados se muestre otra cosa que no sean establecimientos cuya población sea `L'Hospitalet de Llobregat`.

Respuesta que se recibe:
  - `count`: nos dirá el total de resultados que encajan con la búsqueda.
  - `previous` y `next`: nos darán enlaces directos a las páginas anterior y siguiente de resultados
  - `pagina`: en la respuesta, nos informará de la página que estamos obteniendo.
  - `results`: contendrá la lista de establecimientos solicitados. Cada uno de ellos tendrá:
    - `id`
    - `nombre`
    - `direccion`
    - `codigo_postal`
    - `poblacion`
    - `latitud`
    - `longitud`
    - `descripcion`
    - `tipo_establecimiento` → (`1`: establecimientos genéricos, `2`: centros de salud, `3`: ayuntamientos)
    - `creado_por`
    - `actualizado_por`
    - `fecha_creacion`
    - `fecha_actualizacion`
    
## /admin/api/establecimientos/ (POST)
Utilizado para dar de alta nuevos establecimientos.

Parámetros que acepta:

- `nombre`: Nombre del establecimiento a registrar (obligatorio)
- `direccion`: Dirección del establecimiento a registrar (obligatorio)
- `codigo_postal`: código postal del establecimiento a registrar
- `poblacion`: población del establecimiento a registrar 
- `latitud` y `longitud`: coordenadas GPS del establecimiento, cada una en formato `12.345678`. Si se dejan ambas a 0, el sistema tratará de obtenerlas a partir de dirección y población utilizando el servicio gratuito de OpenStreetMaps (Nominatim)
- `email`: email de contacto (no será público en la App)
- `web`: web del establecimiento
- `tipo_establecimiento`: → (`1`: establecimientos genéricos, `2`: centros de salud, `3`: ayuntamientos)


## /admin/api/establecimientos/`[número]`/ (GET)
Obtiene la información del establecimiento con ID `número`. Presenta los datos en el mismo formato que tiene la lista de resultados de una solicitud GET a `/admin/api/establecimientos/`


## /admin/api/establecimientos/`[número]`/ (PUT)
Actualiza la información del establecimiento con ID `número`. Utiliza la misma estructura de datos que en los casos anteriores. Ignora silenciosamente los parámetros que hacen referencia a información que es de solo lectura como `id`, `actualizado_por` o `fecha_actualización`.
