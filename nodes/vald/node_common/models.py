from django.db.models import *
from vamdctap.bibtextools import *

class RefCharField(CharField):
    description = "Subclass to CharField that returns strings split at commas"
    __metaclass__ = SubfieldBase
    def to_python(self, value):
        #tmp = super(RefCharField, self).to_python(self, value)
        if hasattr(value,'split'):
            return value.split(',')
        else:
            return value


class Species(Model):
    id = AutoField(primary_key=True, db_index=True)
    name = CharField(max_length=10, db_index=True)
    ion = PositiveSmallIntegerField(db_index=True)
    inchi = CharField(max_length=32, db_index=True)
    inchikey = CharField(max_length=28, db_index=True)
    mass = DecimalField(max_digits=8, decimal_places=5, db_index=True)
    massno = PositiveSmallIntegerField(null=True, db_index=True)
    ionen = DecimalField(max_digits=10, decimal_places=3, null=True)
    solariso = DecimalField(max_digits=6, decimal_places=4, null=True)
    dissen = DecimalField(max_digits=8, decimal_places=4, null=True)
    ncomp = PositiveSmallIntegerField(null=True)
    atomic = PositiveSmallIntegerField(null=True, db_index=True)
    isotope = PositiveSmallIntegerField(null=True)

    components = ManyToManyField('self',through='SpeciesComp', symmetrical=False) # only used in case of molecules

    def isMolecule(self):
         return self.ncomp and self.ncomp > 1

    def __unicode__(self):
        return u'ID:%s %s'%(self.id,self.name)
    class Meta:
        db_table = u'species'

class SpeciesComp(Model):
    """
    This is just the intermediary model so that species can refer
    to itself to build molecules.
    """
    molecule = ForeignKey(Species,related_name='molec')
    atom = ForeignKey(Species,related_name='atom')
    class Meta:
        db_table = u'species_components'

class Reference(Model):
    id = CharField(max_length=7, primary_key=True, db_index=True)
    bibtex = TextField(null=True)

    def XML(self):
        return BibTeX2XML( self.bibtex )

    class Meta:
        db_table = u'refs'
    def __unicode__(self):
        return u'%s'%self.id

class LineList(Model):
    id = AutoField(primary_key=True, db_index=True)
    references = ManyToManyField(Reference) # handled by external script
    srcfile = CharField(max_length=128)
    srcfile_ref = CharField(max_length=128, null=True)
    speclo = ForeignKey(Species,related_name='islowerboundspecies_source',db_column='speclo',null=True, db_index=False)
    spechi = ForeignKey(Species,related_name='isupperboundspecies_source',db_column='spechi',null=True, db_index=False)
    listtype = PositiveSmallIntegerField(null=True)
    # vald category mapping = {'exp':0, 'obs':1, 'emp':2, 'pred':3, 'calc':4, 'mix':5
    # vald->xsams mapping = {0:'experiment', 1:'semiempirical', 2:'derived', 3:'theory',4:'semiempirical',5:'compilation'}
    method = PositiveSmallIntegerField(null=True, db_index=True) # 0-5
    r1 = PositiveSmallIntegerField(null=True)
    r2 = PositiveSmallIntegerField(null=True)
    r3 = PositiveSmallIntegerField(null=True)
    r4 = PositiveSmallIntegerField(null=True)
    r5 = PositiveSmallIntegerField(null=True)
    r6 = PositiveSmallIntegerField(null=True)
    r7 = PositiveSmallIntegerField(null=True)
    r8 = PositiveSmallIntegerField(null=True)
    r9 = PositiveSmallIntegerField(null=True)
    srcdescr = CharField(max_length=128, null=True)
    def __unicode__(self):
        return u'ID%s: %s'%(self.id,self.srcdescr)
    class Meta:
        db_table = u'linelists'

# Environments
class EnvClass(object):
    def __init__(self,xml):
        self.xml = xml
    def XML(self):
        return self.xml

EnvGeneral="""<Environment envID="%s">
<Comments>%s</Comments>
<Temperature><Value units="K">1.0E4</Value></Temperature>
<TotalNumberDensity><Comments>The broadening parameters are given in
Hz per number density (i.e. cm^3/s), so they can simply
be scaled with the number density. Note also that
actually log10(gamma) is given.</Comments>
<Value units="1/cm3">1</Value>
</TotalNumberDensity>
</Environment>
"""
EnvStark=EnvGeneral%('Evald-stark',"""A given gamma can be scaled with
gamma = gamma_given * (T / T_ref)^1/6 * number density of free electrons.""")
EnvWaals=EnvGeneral%('Evald-waals',"""A given gamma can be scaled with gamma =
gamma_given * (T / T_ref)^alpha * number density for any neutral perturber.
If alpha is not given, it is 1/3""")
#EnvWaals=EnvGeneral%('Evald-waals',"""The broadening can be
#calculated by help of additional parameters, using a more accurate equation by
#Anstee, Barklem & O'Mara.""")
EnvNatural="""<Environment envID="Evald-natural">
<Comments>There are no parameters for natural/radiative broadening.</Comments>
</Environment>"""
Environments = [EnvClass(EnvStark), EnvClass(EnvWaals), EnvClass(EnvNatural)]


# Not yet functional, pending evntual future changes
class FuncClass(object):
    def __init__(self, xml):
        self.xml = xml
    def XML(self):
        return self.xml
# Functions
VALDfuncs = [
FuncClass("""<Function functionID="Fvald-stark">
<Comments>This function gives the temperature dependence of Stark broadening.</Comments>
<Expression computerLanguage="Fortran">
    gammawaal * (T / 10000.0) ** (1.0/6.0) * N
</Expression>
<Y name="gammaL" units="1/cm^3"></Y>
<Arguments>
    <Argument name="T" units="K">
        <Description>The absolute temperature, in K</Description>
    </Argument>
    <Argument name="N" units="1/cm^3">
        <Description>Number density of neutral perturbers</Description>
    </Argument>
</Arguments>
<Parameters>
    <Parameter name="gammawaal" units="cm^3/s">
       <Description>Lorentzian HWHM of the line</Description>
    </Parameter>
</Parameters>
</Function>"""),
FuncClass("""<Function functionID="Fvald-waals">
<Comments>This function gives the temperature dependence of Van der Waals broadening.</Comments>
<Expression computerLanguage="Fortran">
    gammawaal * (T / 10000.0) ** (1.0/3.0) * N
</Expression>
<Y name="gammaL" units="1/cm^3"></Y>
<Arguments>
    <Argument name="T" units="K">
        <Description>The absolute temperature, in K</Description>
    </Argument>
    <Argument name="N" units="1/cm^3">
        <Description>Number density of neutral perturbers</Description>
    </Argument>
</Arguments>
<Parameters>
    <Parameter name="gammawaal" units="cm^3/s">
       <Description>Lorentzian HWHM of the line</Description>
    </Parameter>
</Parameters>
</Function>"""),
FuncClass("""<Function functionID="Fvald-waals_barklem">
<Comments>This function gives the temperature dependence of Van der Waals broadening using a more exact formula by Anstee, Barklem & O'Mara.</Comments>
<Expression computerLanguage="LaTeX">
    \left(\frac{4,\pi}\right)\Gamma\left(\frac{4-\alpha,2}\right)v_0\sigma\left(\frac{\bar{v},1000000}^{(1-\alpha)}\cdot N
</Expression>
<Y name="gammaL" units="1/s"></Y>
<Arguments>
    <Argument name="v" units="cm/s">
        <Description>Collisional speed, in cm/s</Description>
    </Argument>
    <Argument name="N" units="1/cm^3">
        <Description>Number density of neutral perturbers</Description>
    </Argument>
</Arguments>
<Parameters>
    <Parameter name="sigma" units="cm^3/s">
       <Description>Broadening cross section </Description>
    </Parameter>
    <Parameter name="alpha" units="cm^3/s">
       <Description>Velocity dependence of the cross section, assuming \sigma(v) \propto v^{-\alpha}<Description>
    </Parameter>
</Parameters>
<SourceCodeURL>http://www.astro.uu.se/~barklem/howto.html</SourceCodeURL>
</Function>
""")]
