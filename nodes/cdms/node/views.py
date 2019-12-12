# -*- coding: utf-8 -*-

# This is where you would add additional functionality to your node,
# bound to certain URLs in urls.py
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
import json as simplejson

from django.conf import settings

from . import cdmsportalfunc as cpf
from . import forms
from . import models
from django.views.decorators.cache import cache_page

FILENAME_XSAMS2HTML = settings.XSLT_DIR + 'convertXSAMS2html.xslt'
FILENAME_XSAMS2RAD3D = settings.XSLT_DIR + 'convertXSAMS2Rad3d.xslt'
FILENAME_MERGERADEX = settings.XSLT_DIR + 'speciesmergerRadex_1.0_v0.3.xslt'


class QUERY(object):
    """
    """
    requeststring = "sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&"

    def __init__(self,
                 data,
                 baseurl=settings.BASE_URL+settings.TAP_URLPATH,
                 qformat=None):
        self.isvalid = True
        self.errormsg = ''
        # remove white spaces from the right side
        self.baseurl = baseurl.rstrip()
        self.format = qformat

        try:
            self.data = data
        except Exception as e:
            self.isvalid = False
            self.errormsg = 'Could not read argument dict: %s' % e

        if self.isvalid:
            self.validate()

    def validate(self):

        try:
            self.database = self.data.get('database', 'cdms')
        except Exception:
            self.database = 'cdms'
        try:
            self.freqfrom = self.data.get('T_SEARCH_FREQ_FROM', 0)
        except Exception:
            self.freqfrom = 0
        try:
            self.freqto = self.data.get('T_SEARCH_FREQ_TO', 0)
        except Exception:
            self.freqto = 0
        try:
            self.minint = self.data.get('T_SEARCH_INT', -10)
        except Exception:
            self.minint = -10

        try:
            self.IntUnit = self.data.get('IntUnit', 'T300')
        except Exception:
            self.IntUnit = 'T300'

        try:
            self.orderby = self.data.get('T_SORT', '')
        except Exception:
            self.orderby = ''

        try:
            self.explines = self.data.get('T_SHOWEXPLINES', 'merge')
        except Exception:
            self.explines = 'merge'

        if not self.format:
            try:
                self.format = self.data.get('T_TYPE', 'XSAMS')
            except Exception:
                self.format = 'XSAMS'

        try:
            self.url = self.data.get('queryURL', '')
        except Exception:
            self.url = ''

        if len(self.url) == 0:
            try:
                self.query = self.data.get('QUERY', "").rstrip()
            except Exception:
                self.query = ""
            if self.query.strip() == 'SELECT ALL WHERE':
                self.query = 'SELECT SPECIES'
            try:
                self.url = self.baseurl \
                         + self.requeststring \
                         + QueryDict("QUERY=" + self.query).urlencode()
            except Exception:
                self.url = None

        if len(self.orderby) > 0 and 'ORDERBY' not in self.url:
            self.url += '&ORDERBY=%s' % self.orderby

        if self.data.get('IntUnit', 'T300') == 'A':
            self.url += '&IntUnit=A'
        # speciesID identifies only CDMS/JPL species
        try:
            self.speciesIDs = self.data.getlist('speciesIDs')
        except Exception:
            self.speciesIDs = []

        # inchikey is used to identify isotopologs
        try:
            self.inchikey = self.data.getlist('inchikey')
        except Exception:
            self.inchikey = []

        # Molecules are currently identified via StoichiometricFormula
        try:
            self.molecule = self.data.getlist('molecule')
        except Exception:
            self.molecule = []

        if self.format == 'spcat':
            if self.explines == 'merge':
                self.url = self.url.replace(
                        'XSAMS', 'mrg').replace(
                                "ALL", "RadiativeTransitions")
            else:
                self.url = self.url.replace(
                        'XSAMS', 'spcat').replace(
                                "ALL", "RadiativeTransitions")

        # this is slightly different to spcat and uses correct qn labels
        if self.format == 'comfort':
            self.url = self.url.replace(
                    'XSAMS', 'xspcat').replace("ALL", "RadiativeTransitions")

        if self.format == 'png':
            self.url = self.url.replace(
                    'XSAMS', 'png').replace("ALL", "RadiativeTransitions")

        # used only for radex:
        if self.format == 'rad3d':
            self.spec_url = self.data.get('spec_url', '')
            self.spec_speciesid = self.data.get('spec_speciesid', '')
            self.col_url = self.data.get('col_url', '')
            self.col_speciesid = self.data.get('col_speciesid', '')


def index(request):
    return render(request, 'cdmsportal/home.html')


def contact(request):
    return render(request, 'cdmsportal/contact.html')


@cache_page(60 * 15)
def general(request):
    return render(request, 'cdmsportal/general.html')


def help(request):
    return render(request, 'cdmsportal/help.html')


def queryPage(request):
    """
    Creates the Form to define query parameters;
    Species are already defined and should be posted to this page
    """
    postvars = request.POST
    id_list = request.POST.getlist('speciesIDs')
    inchikey_list = request.POST.getlist('inchikey')
    stoichio_list = request.POST.getlist('molecule')
    species_list = cpf.get_species_list(id_list, database=-5)
    isotopolog_list = models.Species.objects.filter(inchikey__in=inchikey_list)
    molecule_list = models.Species.objects.filter(
            molecule__stoichiometricformula__in=stoichio_list)

    context = {"postvar": postvars,
               "speciesid_list": id_list,
               "inchikey_list": inchikey_list,
               "stoichio_list": stoichio_list,
               "species_list": species_list,
               "isotopolog_list": isotopolog_list,
               "molecule_list": molecule_list,
               }

    return render(request, 'cdmsportal/queryForm.html', context)


def query_form(request):
    """
    Create the species selection - page from the species (model) stored in the
    database
    """
    id_list = request.POST.getlist('speciesIDs')
    inchikey_list = request.POST.getlist('inchikey')
    stoichio_list = request.POST.getlist('molecule')
    context = {"action": "queryPage",
               "speciesid_list": id_list,
               "inchikey_list": inchikey_list,
               "stoichio_list": stoichio_list,
               }
    return render(request, 'cdmsportal/querySpeciesAjax.html', context)


def tools(request):
    """
    """
    if request.method == 'POST':
        form = forms.XsamsConversionForm(request.POST, request.FILES)
        if form.is_valid():

            response = HttpResponse(
                    form.cleaned_data['result'],
                    content_type='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename=%s.%s' \
                % (form.cleaned_data.get('infile') or 'output',
                   form.cleaned_data.get('format'))
            return response
        else:
            print("(cdms/tools) INVALID RESPONSE")

    else:
        form = forms.XsamsConversionForm()

    context = {'form': form}
    return render(request, 'cdmsportal/tools.html', context)


def selectSpecie(request):
    """
    Create the species selection - page from the species (model) stored in the
    database
    """
    species_list = cpf.get_species_list()
    context = {"action": "catalog", "species_list": species_list}
    return render(request, 'cdmsportal/selectSpecies.html', context)


def selectSpecie2(request):
    """
    Create the species selection - page from the species (model) stored in the
    database
    """
    context = {"action": "catalog"}
    return render(request, 'cdmsportal/selectSpeciesAjax.html', context)


def html_list(request, content='species'):
    """
    Renders species, molecules, or isotopologs as html_list,
    which can be included into webpages via ajax request.

    content: string ('species' - default, 'molecules', 'isotopologs'
             which specifies which information will be returned.

    Returns html_string
    """
    if content == 'molecules':
        molecules_list = cpf.get_molecules_list()
        context = {"action": "catalog",
                   "species_list": [],
                   "molecules_list": molecules_list,
                   "isotopolog_list": [],
                   }

        return render(request, 'cdmsportal/species_table.html', context)

    elif content == 'isotopologs':
        isotopolog_list = cpf.get_isotopologs_list()
        context = {"action": "catalog",
                   "species_list": [],
                   "molecules_list": [],
                   "isotopolog_list": isotopolog_list,
                   }

        return render(request, 'cdmsportal/species_table.html', context)

    else:
        species_list = cpf.get_species_list()
        context = {"action": "catalog",
                   "species_list": species_list,
                   "molecules_list": [],
                   "isotopolog_list": [],
                   }

    return render(request, 'cdmsportal/species_table.html', context)


@cache_page(60*15)
def json_list(request, content='species'):
    """
    Creates a list of species available in the database.
    if field database is posted, the list is restricted to species with
    origin == database

    database: corresponds to origin - field in db (0:jpl, 5:cdms, <0: all)

    returns type(<json>) list of species with species data.
    """
    try:
        db = int(request.POST.get('database', 5))
    except ValueError:
        db = 5

    response_dict = {}
    species_list = []
    error = ''
    for specie in cpf.get_species_list(database=db):
        try:
            s = {'id': specie.id,
                 'molecule': specie.molecule.id,
                 'structuralformula': specie.molecule.structuralformula,
                 'stoichiometricformula':
                 specie.molecule.stoichiometricformula,
                 'moleculesymbol': specie.molecule.symbol,
                 # 'atom':specie.atom,
                 'speciestag': specie.speciestag,
                 'name': specie.name,
                 'trivialname': specie.molecule.trivialname,
                 'isotopolog': specie.isotopolog,
                 'state': specie.state,
                 'state_html': specie.state_html(),
                 'inchikey': specie.inchikey,
                 'contributor': specie.contributor,
                 'version': specie.version,
                 'dateofentry': str(specie.dateofentry),
                 }
            species_list.append(s)
        except Exception as e:
            print("Error: %s" % str(e))
            error = e

    response_dict.update({'species': species_list,
                          'database': db,
                          'error': error})

    return HttpResponse(simplejson.dumps(response_dict),
                        content_type='application/json')


def catalog(request, id=None):
    """
    Creates the documentation page for a specie

    id: Database id of the specie
    """

    if id is None:
        # get the species id from posted values
        id = request.POST.get("T_EID", 0)
        # if nothing has been posted, get the first specie by tag-number
        if id == 0:
            specie = models.Species.objects.all().order_by('speciestag')[0]
            id = specie.id

    # query specie from database
    specie = cpf.getSpecie(id)

    # query sources from database
    sources = cpf.getSources4specie(id)

    # query datasets from database
    datasets = cpf.getDatasets4specie(id)

    # query parameters from database
    rotationalConstants = cpf.getParameters4specie(id, "Rotational Constant")
    dipoleMoments = cpf.getParameters4specie(id, "Dipole Moment")
    otherParameters = cpf.getParameters4specie(id, "Other")

    pfhtml = cpf.getPartitionf4specie(id)
    nuclear_spin_isomers = models.NuclearSpinIsomers.objects.filter(specie=id)
    for nsi in nuclear_spin_isomers:
        pfhtml += "<br><br>" + cpf.getPartitionf4specie(id, nsi=nsi)

    # query files from database
    files = cpf.getFiles4specie(id)

    context = {"specie": specie,
               "sources": sources,
               "datasets": datasets,
               "files": files,
               "rotationalconstants": rotationalConstants,
               "dipolemoments": dipoleMoments,
               "pfhtml": pfhtml,
               "otherparameters": otherParameters,
               "PORTAL_URLPATH": settings.BASE_URL + '/cdms/portal/',
               "BASE_URL": settings.BASE_URL,
               "TAP_URLPATH": '/cdms/tap/',
               }

    return render(request, 'cdmsportal/showDocumentation.html', context)


def showResults(request):
    """
    Returns the 'Result' - page. The result itself is retrieved via ajax
    request.
    """

    postvars = QUERY(request.POST)

    result = ""
    if postvars.database == 'vamdc':
        readyfunc = 'ajaxGetNodeList();ajaxQueryNodeContent();'
    else:
        readyfunc = 'ajaxQueryNodeContent();'

    try:
        context = {"postvars": postvars,
                   "result": result,
                   "readyfunc": readyfunc}
    except UnicodeError:
        context = {"postvars": postvars, "result": result}
        return render(request, 'cdmsportal/showResults2.html', context)

    except Exception as err:
        context = {"postvars": postvars, "result": err}

    try:
        return render(request, 'cdmsportal/showResults2.html', context)
    except UnicodeError:
        context = {"postvars": postvars, "result": result}
        return render(request, 'cdmsportal/showResults2.html', context)
    except Exception as err:
        context = {"postvars": postvars, "result": err}
        return render(request, 'cdmsportal/showResults2.html', context)


def ajaxRequest(request):
    """
    """
    postvars = request.POST
    response_dict = {}
    if 'function' in request.POST:

        if request.POST['function'] == 'checkQuery':
            QUERYs, htmlcode = cpf.check_query(request.POST)
            response_dict.update({'QUERY': QUERYs,
                                  'htmlcode': htmlcode,
                                  'message': " Tach "})
        elif request.POST['function'] == 'getVAMDCstats':
            htmlcode, nodes = cpf.getHtmlNodeList()
            response_dict.update({'htmlcode': htmlcode,
                                  'nodes': nodes,
                                  'message': " Statistics "})
        elif request.POST['function'] == 'ajaxQuery':
            # get result and return it via ajax
            # just apply the stylesheet if a complete url has been posted
            baseurl = request.POST.get('nodeurl',
                                       settings.BASE_URL
                                       + settings.TAP_URLPATH)

            if 'url2' in request.POST:
                htmlcode = str(cpf.applyStylesheet(request.POST['url2'],
                                                   xsl=FILENAME_XSAMS2HTML))
            else:
                postvars = QUERY(request.POST, baseurl=baseurl)
                if postvars.url:
                    if postvars.format.lower() == 'xsams':
                        htmlcode = \
                                str(cpf.applyStylesheet(
                                      postvars.url,
                                      xsl=FILENAME_XSAMS2HTML))
                    elif postvars.format == 'rad3dx':
                        htmlcode = "<pre>" \
                                + str(cpf.applyStylesheet(
                                        postvars.url,
                                        xsl=FILENAME_XSAMS2HTML)) + "</pre>"
                    elif postvars.format == 'rad3d':
                        # output = str(applyRadex(
                        #       postvars.url, xsl = FILENAME_MERGERADEX))
                        output = str(cpf.applyRadex(
                            postvars.spec_url,
                            species1=postvars.spec_speciesid,
                            species2=postvars.col_speciesid,
                            inurl2=postvars.col_url))
                        htmlcode = "<pre>" + output + "</pre>"
                    elif postvars.format == 'png':
                        htmlcode = "<img class='full' width='100%' src=" \
                                   + postvars.url \
                                   + " alt='Stick Spectrum'>"
                    else:
                        htmlcode = "<pre>" \
                                + cpf.geturl(postvars.url).decode('utf-8') \
                                + "</pre>"
                else:
                    htmlcode = "<p> Invalid request </p>"

            response_dict.update({'QUERY': "QUERY",
                                  'htmlcode': htmlcode,
                                  'message': " Statistics "})

        elif request.POST['function'] == 'getNodeStatistic':
            # get url of the node which should have been posted
            nodeurl = request.POST.get('nodeurl', "")
            inchikey = request.POST.get('inchikey', "")

            postvars = QUERY(request.POST, baseurl=nodeurl, qformat='XSAMS')
            # fetch statistic for this node
            if nodeurl:
                htmlcode, vc = cpf.getNodeStatistic(nodeurl,
                                                    inchikey,
                                                    url=postvars.url)
            else:
                htmlcode = ""
                vc = {}

            try:
                numspecies = vc['vamdccountspecies']
            except Exception:
                numspecies = '0'

            response_dict.update({'htmlcode': htmlcode,
                                  'message': " Statistics ", })
            response_dict.update(vc)
        elif request.POST['function'] == 'queryspecies':
            nodeurl = request.POST.get('nodeurl', "")
            inchikey = request.POST.get('inchikey', "")

            postvars = QUERY(request.POST, baseurl=nodeurl, qformat='XSAMS')
            if not ('hitran' in postvars.url or 'umist3' in postvars.url):
                url = postvars.url.replace('ALL', 'SPECIES').replace(
                        'RadiativeTransitions', 'SPECIES')
            else:
                url = postvars.url
            url = url.replace('rad3d', 'XSAMS')
            url = url.replace('xspcat', 'XSAMS')
            url = url.replace('spcat', 'XSAMS')
            url = url.replace('mrg', 'XSAMS')
            url = url.replace('png', 'XSAMS')
            url = url.replace('comfort', 'XSAMS')
            try:
                result, speciesdata = cpf.getspecies(url)
            except Exception:
                result, speciesdata = "<p> Invalid request </p>", []

            response_dict.update({'htmlcode': result,
                                  'speciesdata': speciesdata,
                                  'message': " Species ", })
        else:
            response_dict.update({'QUERY': QUERYs,
                                  'htmlcode': "<p> HALLO </p>",
                                  'message': " Tach "})
    else:
        response_dict.update({'QUERY': "",
                              'htmlcode': "Error: No function name posted! ",
                              'message': "Error: No function name posted! "})

    return HttpResponse(simplejson.dumps(response_dict),
                        content_type='application/json')


def specieslist(request):
    """
    Create the species selection - page for the admin-site from the species
    (model) stored in the database
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(settings.BASE_URL+settings.PORTAL_URLPATH
                                    + 'login/?next=%s' % request.path)

    species_list = cpf.get_species_list()
    context = {"action": "catalog", "species_list": species_list}
    return render(request, 'cdmsadmin/selectSpecies.html', context)


def queryspecies(request, baseurl=settings.BASE_URL + settings.TAP_URLPATH):

    requeststring = \
            "sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=SELECT+SPECIES"
    url = baseurl + requeststring

    try:
        result = cpf.getspecies(url)
    except Exception:
        result = "<p> Invalid request </p>"

    context = {"result": result}
    return render(request, 'cdmsportal/showResults.html', context)


def getfile(request, id):
    """
    reads the content from an ascii-file from the database
    and returns the file

    id: Database id of the file
    """
    f = models.Files.objects.get(pk=id)
    response = HttpResponse(f.asciifile, content_type='text/txt')

    response['Content-Disposition'] = 'attachment; filename=%s' % (f.name)

    return response


def download_data(request):
    postvars = request.POST

    baseurl = request.POST.get('nodeurl',
                               settings.BASE_URL + settings.TAP_URLPATH)

    if 'url2' in request.POST:
        return HttpResponseRedirect(request.POST['url2'])
    else:
        postvars = QUERY(request.POST, baseurl=baseurl)
        if postvars.url:
            if postvars.format.lower() == 'xsams':
                return HttpResponseRedirect(postvars.url)


def cdms_lite_download(request):
    """
    Returns the cdms_lite (sqlite3) database file
    """
    return HttpResponseRedirect(settings.BASE_URL
                                + '/static/cdms/cdms_lite.db.gz')


def recommendation_list(request):
    """
    Returns a list of recommended entries (JPL - CDMS)
    """
    s = cpf.listRecommendedEntries()

    return HttpResponse(s, content_type='text/plain')


def is_recommended(request, id):
    """
    Checks if an entry is recommended.
    """

    ret_value = cpf.isRecommended(id)

    return HttpResponse(ret_value, content_type='text/plain')
