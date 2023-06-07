from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from admin_api.models import Establecimiento
from core import settings
from .forms import NouEstablimentForm, EditaEstablimentForm
import requests
import logging

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


# Create your views here.
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    # Calc some stats:
    establishments_alltypes_total = Establecimiento.objects.filter(activo=True).count()
    establishments_disabled_total = Establecimiento.objects.filter(activo=False).count()
    establishments_type1_total = Establecimiento.objects.filter(activo=True).filter(
        tipo_establecimiento_id=1).count()
    establishments_type2_total = Establecimiento.objects.filter(activo=True).filter(
        tipo_establecimiento_id=2).count()
    establishments_type3_total = Establecimiento.objects.filter(activo=True).filter(
        tipo_establecimiento_id=3).count()
    context['establishments_alltypes_total'] = establishments_alltypes_total
    context['establishments_disabled_total'] = establishments_disabled_total
    context['establishments_type1_total'] = establishments_type1_total
    context['establishments_type2_total'] = establishments_type2_total
    context['establishments_type3_total'] = establishments_type3_total
    # Calc some issues:
    establishments_no_coords = Establecimiento.objects.filter(
        models.Q(latitud=0) &
        models.Q(longitud=0)).filter(activo=True).count()
    establishments_no_cp = Establecimiento.objects.filter(
        models.Q(codigo_postal=0) |
        models.Q(codigo_postal=None) |
        models.Q(codigo_postal='')).filter(activo=True).count()

    context['establishments_no_cp'] = establishments_no_cp
    context['establishments_no_coords'] = establishments_no_coords

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    # noinspection PyBroadException
    try:
        load_template = request.path.split('/')[-1]
        # Provided all the necessary contexts for each different page
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def afegir_establiment(request):
    context = {
        'form': NouEstablimentForm()
    }

    if request.method == 'POST':
        formulario = NouEstablimentForm(data=request.POST)
        if formulario.is_valid():
            nuevo_establecimiento = formulario.save()
            context['feedback_message'] = "Establiment afegit correctament. A continuació pots editar més detalls."
            context['id'] = nuevo_establecimiento.id
            return render(request, 'establiments/detall.html', context)
        else:
            context['form'] = formulario
            context['feedback_message'] = "Dades no vàlides o incomplertes."
            return render(request, 'establiments/afegir.html', context)
    return render(request, 'establiments/afegir.html', context)


@login_required(login_url="/login/")
@require_http_methods("GET")
def llistat_establiments(request):
    # just for aesthetics and avoiding the "GET.get" thing
    requestparams = request.GET.copy()
    # Listing preservation logic
    # torna is used as a trigger for recovery stored parameters (i.e.: when returning to listings from an item edition)
    torna = requestparams.get('torna', 0)
    last_listing_url = request.session.get('last_listing_url', None)
    if torna == "1" and last_listing_url is not None:
        logger.debug(f'Redirecting to {last_listing_url} as per session stored parameter')
        del request.session['last_listing_url']
        return redirect(last_listing_url)

    # queryset selection stuff
    initial_queryset = Establecimiento.objects.filter(activo=True)
    llistat = requestparams.get('llistat')
    if llistat:
        if llistat == 'sense-cp':
            establiments = initial_queryset.filter(models.Q(codigo_postal=None) |
                                                   models.Q(codigo_postal=0)
                                                   ).order_by('-id')
        elif llistat == 'sense-gps':
            establiments = initial_queryset.filter((models.Q(latitud=0) & models.Q(longitud=0)) |
                                                   models.Q(latitud=None) |
                                                   models.Q(longitud=None)
                                                   ).order_by('-id')
        elif llistat == 'inactius':
            establiments = Establecimiento.objects.filter(activo=False).order_by('-id')
        elif llistat == 'establiments-generals':
            establiments = Establecimiento.objects.filter(tipo_establecimiento_id=1).order_by('-id')
        elif llistat == 'ajuntaments':
            establiments = Establecimiento.objects.filter(tipo_establecimiento_id=3).order_by('-id')
        elif llistat == 'hospitals-centres-salut':
            establiments = Establecimiento.objects.filter(tipo_establecimiento_id=2).order_by('-id')
        else:
            messages.add_message(request, messages.WARNING, 'S\'ha demanat un llistat especial que no existeix. '
                                                            'Es mostra un llistat de tots els establiments.')
            establiments = initial_queryset.order_by('-id')
    else:
        buscar = requestparams.get('buscar')
        if buscar:
            establiments = initial_queryset.filter(models.Q(nombre__icontains=buscar) |
                                                   models.Q(direccion__icontains=buscar) |
                                                   models.Q(codigo_postal__icontains=buscar) |
                                                   models.Q(poblacion__icontains=buscar)
                                                   ).order_by('-id')
        else:
            establiments = initial_queryset.order_by('-id')

    # amount of results - must go BEFORE pagination stuff
    amount = len(establiments)

    # pagination stuff
    pagina = requestparams.get('pagina', 1)
    try:
        paginator = Paginator(establiments, 100)
        establiments = paginator.page(pagina)
    except (PageNotAnInteger, EmptyPage):
        raise Http404

    # listing preservation logic 2
    # If listing procedure was ok, we store the parameters in session
    # so we can come back exactly to the same place in case we go to an establishment detail sheet, edit something,
    # and come back
    last_listing_url = request.build_absolute_uri()
    logger.debug(f'Storing in session: last_listing_url = {last_listing_url}')
    request.session[f'last_listing_url'] = last_listing_url
    # / listing preservation logic 2

    context = {
        'entity': establiments,
        'amount': amount,
        'request': request.GET,
        'paginator': paginator
    }
    return render(request, 'establiments/llistat.html', context)


@login_required(login_url="/login/")
def detall_establiment(request):
    req_id = request.GET.get('id', None)
    msg_no_id = 'No s\'ha indicat cap identificador d\'establiment.'
    msg_no_establishment = 'No s\'ha trobat un establiment amb l\'identificador indicat'
    msg_invalid_id = 'Identificador d\'establiment invàlid'
    msg_invalid_data = '<b>Dades no vàlides o incomplertes:</b> Si us plau, revisa els valors del formulari o ' \
                       'cancel·la l\'edició de l\'establiment.'
    msg_edited_ok = 'Establiment editat correctament.'
    if not req_id:
        messages.error(request, msg_no_id)
        return redirect('/establiments/llistat/')
    try:
        req_id = int(req_id)
    except (ValueError, TypeError):
        messages.error(request, msg_invalid_id)
        return redirect('/establiments/llistat/')
    establecimiento = Establecimiento.objects.all().filter(id=req_id).first()
    if not establecimiento:
        messages.error(request, msg_no_establishment)
        return redirect('/establiments/llistat/')
    # id ok and establisment found
    form = EditaEstablimentForm(instance=establecimiento)
    # needsgpscords will be true if both coordinates are 0. User can force re-retrieval of coordinates setting both to 0
    needsgpscoords = establecimiento.latitud == establecimiento.longitud == 0
    needspostalcode = (establecimiento.codigo_postal is None or establecimiento.codigo_postal == "")
    context = {
        'id': req_id,
        'form': form,
        'needsgpscoords': needsgpscoords,
        'needspostalcode': needspostalcode,
        'creado_por': establecimiento.creado_por,
        'fecha_creacion': establecimiento.fecha_creacion,
        'actualizado_por': establecimiento.actualizado_por,
        'fecha_actualizacion': establecimiento.fecha_creacion,
        # 'google_api_key': settings.GOOGLE_API_KEY
    }
    if request.method == 'POST':
        form = EditaEstablimentForm(data=request.POST, instance=Establecimiento.objects.get(id=req_id))
        if form.is_valid():
            establecimiento_editado = form.save()
            establecimiento_editado.fecha_actualizacion = timezone.now()
            establecimiento_editado.actualizado_por = get_user(request).username
            establecimiento_editado.save()
            messages.success(request, msg_edited_ok)
            return redirect(f'/establiments/detall/?id={req_id}')
        else:
            context['form'] = form
            context['feedback_message'] = msg_invalid_data
            return redirect(f'/establiments/detall/?id={req_id}')

    return render(request, 'establiments/detall.html', context)


# GOOGLE MAPS APIs PROXY
def user_is_authenticated(user):
    return user.is_authenticated


@csrf_exempt
@user_passes_test(user_is_authenticated)
def googlemapsproxy(request):
    # get path that needs to be part of real request to google maps apis
    # CAUTION: this only works when the view is attached to a 1st level URL
    # i.e.: https://nopucesperar.org/googlemapsproxy
    # and the requests are made with leading slash i.e.: "/googlemapsproxy"
    # attaching the view to deeper levels will cause bad url requested to google
    # i.e.: https://nopucesperar.org/this/wont/work/googlemapsproxy will trigger a request to
    # https://maps.googleapis.com/maps/api/wont/work/googlemapsproxy
    request_path = "/".join(request.path.split("/")[2:])
    logger.debug(f'(PROXY) Requested path: {request_path}')
    calculated_url = f'https://maps.googleapis.com/maps/api/{request_path}'
    logger.debug(f'(PROXY) Calculated url: {calculated_url}')

    proxy_request_kwargs = {
        'method': request.method,
        'url': calculated_url,
        'params': request.GET.copy() if request.method == 'GET' else {},
        'data': request.POST.copy() if request.method == 'POST' else {},
        # 'headers': request.headers,
    }

    if request.method == 'GET':
        proxy_request_kwargs['params']['key'] = settings.GOOGLE_API_KEY
    elif request.method == 'POST':
        proxy_request_kwargs['data']['key'] = settings.GOOGLE_API_KEY
    # logger.debug(f'GOOGLE MAPS PROXY: Making request to {calculated_url} with params {proxy_request_kwargs}')
    response = requests.request(**proxy_request_kwargs)
    content_type = response.headers['Content-Type']
    proxy_response = HttpResponse(
        content=response.content,
        status=response.status_code,
        content_type=content_type
    )
    logger.debug(f'(PROXY) Content type of proxified request has been {content_type}')

    '''
    # well, you can't copy all headers as if nothing...
    for header, value in response.headers.items():
        proxy_response[header] = value
    '''

    return proxy_response
