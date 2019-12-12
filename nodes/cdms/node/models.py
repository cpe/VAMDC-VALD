# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field
# names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom
# [appname]' into your database.
from django.db import models
from django.db import connection
# from vamdctap.bibtextools import *
from node.latex2html import latex2html
import numpy as np

FILTER_DICT = {}
# References which will always be returned
DATABASE_REFERENCES = [1921]


def formatstring(value, format, noneformat):
    if value is not None:
        return format % value
    else:
        return noneformat % ""


def formatqn(value):
    if value is None:
        return ''
    elif value > 99 and value < 360:
        return chr(55 + value // 10) + "%01d" % (value % 10)
    elif value < -9 and value > -260:
        return chr(95 - (value - 1) // 10) + "%01d" % - (value % -10)
    else:
        return str(value)


def format_degeneracy(value):
    if value is None:
        return ''
    elif value > 999 and value < 3600:
        return chr(55+value/100) + "%02d" % (value % 100)
    else:
        return str(value)


class Molecules(models.Model):
    """
    The Molecules class contains general information of the species. It is on
    top of the species class and collects data which is general for all
    isotopologs of a molecule.
    """
    id = models.IntegerField(primary_key=True, db_column='M_ID')
    name = models.CharField(max_length=200, db_column='M_Name', blank=True)
    symbol = models.CharField(max_length=250, db_column='M_Symbol', blank=True)
    cas = models.CharField(max_length=20, db_column='M_CAS', blank=True)
    stoichiometricformula = models.CharField(
        max_length=200, db_column='M_StoichiometricFormula', blank=True)
    structuralformula = models.CharField(
        max_length=200, db_column='M_StructuralFormula', blank=True)
    trivialname = models.CharField(
        max_length=200, db_column='M_TrivialName', blank=True)
    numberofatoms = models.CharField(
        max_length=20, db_column='M_NumberOfAtoms', blank=True)
    elementsymbol = models.CharField(
        max_length=3, db_column='M_ElementSymbol', blank=True)
    formalcharge = models.IntegerField(db_column='M_FormalCharge', blank=True)
    comment = models.TextField(db_column='M_Comment', blank=True)

    class Meta:
        db_table = u'Molecules'


class DictAtoms(models.Model):
    """
    This table contains a list of atoms and some of their properties.
    """
    id = models.IntegerField(primary_key=True, db_column='DA_ID')
    name = models.CharField(max_length=50, db_column='DA_Name', blank=True)
    symbol = models.CharField(max_length=10, db_column='DA_Symbol', blank=True)
    element = models.CharField(
            max_length=10, db_column='DA_Element', blank=True)
    massnumber = models.IntegerField(db_column='DA_MassNumber', blank=True)
    mass = models.FloatField(db_column='DA_Mass', blank=True)
    abundance = models.FloatField(db_column='DA_Abundance', blank=True)
    mostabundant = models.IntegerField(
            db_column='DA_MostAbundant', blank=True)
    massreference = models.IntegerField(
            db_column='DA_MassReference', blank=True)
    nuclearcharge = models.IntegerField(
            db_column='DA_NuclearCharge', blank=True)

    class Meta:
        db_table = u'Dict_Atoms'


class Species(models.Model):
    """
    The species class contains information about a species-entry. One
    isotopolog might have more than one entry. These could be different
    electronic or vibrational states or simply archived entries related to
    outdated versions of the specie (outdated versions are kept and not
    deleted).
    """

    RECOMMENDATION_CHOICES = (
        (0, 'recommended'),
        (1, 'same entry as recommended one'),
        (99, 'not recommended'),
    )

    id = models.IntegerField(primary_key=True, db_column='E_ID')
    molecule = models.ForeignKey(
            Molecules, db_column='E_M_ID', on_delete=models.DO_NOTHING)
    atom = models.ForeignKey(
            DictAtoms, db_column='E_DA_ID', on_delete=models.DO_NOTHING)
    speciestag = models.IntegerField(db_column='E_TAG')
    name = models.CharField(max_length=200, db_column='E_Name')
    isotopolog = models.CharField(max_length=100, db_column='E_Isotopomer')
    massnumber = models.IntegerField(db_column='E_MassNumber')
    state = models.CharField(max_length=200, db_column='E_States')
    linearsymasym = models.CharField(
            max_length=20, db_column='E_LinearSymAsym')
    shell = models.CharField(max_length=20, db_column='E_Shell')
    inchi = models.CharField(max_length=200, db_column='E_Inchi')
    inchikey = models.CharField(max_length=100, db_column='E_InchiKey')
    origin = models.IntegerField(db_column='E_Origin')
    contributor = models.CharField(max_length=200, db_column='E_Contributor')
    version = models.CharField(max_length=5, db_column='E_Version')
    dateofentry = models.DateField(db_column='E_DateOfEntry')
    comment = models.TextField(db_column='E_Comment')
    archiveflag = models.IntegerField(db_column='E_Archive')
    recommendationflag = models.IntegerField(
        db_column='E_Recommendationflag', choices=RECOMMENDATION_CHOICES)
    dateactivated = models.DateField(db_column='E_DateActivated')
    datearchived = models.DateField(db_column='E_DateArchived')
    changedate = models.DateTimeField(db_column='E_ChangeDate')

    class Meta:
        db_table = u'Entries'

    # def getMassNumber(self):
    #     tag = str(self.speciestag)
    #     return tag[:-3] #self.speciestag[:-3]

    def CML(self):
        """
        Return the CML version of the molecular structure.
        Use the database function F_GetCML to get the string
        """
        cursor = connection.cursor()
        cursor.execute("SELECT F_GetCML4XSAMS(%s) as cml ", [self.id])
        return cursor.fetchone()[0]

    def get_shortcomment(self):
        return "%6s- v%2s:%s; %s" % (self.speciestag,
                                     self.version,
                                     self.isotopolog,
                                     self.state)

    cmlstring = property(CML)
    # massnumber = property(getMassNumber)
    shortcomment = property(get_shortcomment)

    def state_html(self):
        return latex2html(self.state)


class Datasets(models.Model):
    """
    This class contains the datasets for each specie. A dataset is a header for
    either calculated transitions, experimental transitions or states.
    """
    id = models.IntegerField(primary_key=True, db_column='DAT_ID')
    specie = models.ForeignKey(
            Species, db_column='DAT_E_ID', on_delete=models.DO_NOTHING)
    userid = models.IntegerField(db_column='DAT_U_ID')
    fileid = models.IntegerField(db_column='DAT_FIL_ID')
    speciestag = models.IntegerField(db_column='DAT_E_Tag')
    qntag = models.IntegerField(db_column='DAT_QN_Tag')
    comment = models.TextField(db_column='DAT_Comment')
    name = models.CharField(max_length=100, db_column='DAT_Name')
    type = models.CharField(max_length=10, db_column='DAT_Type')
    public = models.IntegerField(db_column='DAT_Public')
    archiveflag = models.IntegerField(db_column='DAT_Archive')
    hfsflag = models.IntegerField(db_column='DAT_HFS')
    createdate = models.DateField(db_column='DAT_Createdate')
    activateddate = models.DateField(db_column='DAT_Date_Activated')
    archvieddate = models.DateField(db_column='DAT_Date_Archived')

    class Meta:
        db_table = u'Datasets'


class NuclearSpinIsomers(models.Model):
    """
    This class contains informations on nuclear spin isomers.
    """
    id = models.IntegerField(primary_key=True, db_column='NSI_ID')
    specie = models.ForeignKey(
            Species, db_column='NSI_E_ID', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=45, db_column='NSI_Name')
    lowestrovibsym = models.CharField(
            max_length=45, db_column='NSI_LowestRoVibSym')
    symmetrygroup = models.CharField(
            max_length=45, db_column='NSI_SymmetryGroup')
    lowestrovibstate = models.IntegerField(db_column='NSI_LowestRoVib_EGY_ID')

    class Meta:
        db_table = u'NuclearSpinIsomers'

    def lowestrovibstateid(self):
        return '%s-origin-%s' % (self.lowestrovibstate, self.specie_id)


class States(models.Model):
    """
    This class contains the states of each specie.
    """
    id = models.IntegerField(primary_key=True, db_column='EGY_ID')
    specie = models.ForeignKey(
            Species, db_column='EGY_E_ID', on_delete=models.DO_NOTHING)
    speciestag = models.IntegerField(db_column='EGY_E_Tag')
    dataset = models.ForeignKey(
            Datasets, db_column='EGY_DAT_ID', on_delete=models.DO_NOTHING)
    energy = models.FloatField(null=True, db_column='EGY_Energy')
    uncertainty = models.FloatField(null=True, db_column='EGY_Uncertainty')
    energyorigin = models.IntegerField(db_column='EGY_EnergyOrigin_EGY_ID')
    mixingcoeff = models.FloatField(null=True, db_column='EGY_PMIX')
    block = models.IntegerField(db_column='EGY_IBLK')
    index = models.IntegerField(db_column='EGY_INDX')
    degeneracy = models.IntegerField(db_column='EGY_IDGN')
    nuclearstatisticalweight = models.IntegerField(
        db_column='EGY_NuclearStatisticalWeight')
    nsi = models.ForeignKey(
            NuclearSpinIsomers,
            db_column='EGY_NSI_ID',
            on_delete=models.CASCADE)
    nuclearspinisomer = models.CharField(
        max_length=10, db_column='EGY_NuclearSpinIsomer')
    nuclearspinisomersym = models.CharField(
        max_length=45, db_column='EGY_NuclearSpinIsomerSym')
    nsioriginid = models.IntegerField(db_column='EGY_NSI_LowestEnergy_EGY_ID')
    msgroup = models.CharField(max_length=45, db_column='EGY_MS_Group')
    qntag = models.IntegerField(db_column='EGY_QN_Tag')
    qn1 = models.IntegerField(db_column='EGY_QN1')
    qn2 = models.IntegerField(db_column='EGY_QN2')
    qn3 = models.IntegerField(db_column='EGY_QN3')
    qn4 = models.IntegerField(db_column='EGY_QN4')
    qn5 = models.IntegerField(db_column='EGY_QN5')
    qn6 = models.IntegerField(db_column='EGY_QN6')
    user = models.CharField(
            max_length=40, db_column='EGY_User')      # obsolete
    timestamp = models.IntegerField(db_column='EGY_TIMESTAMP')

    class Meta:
        db_table = u'Energies'
        ordering = ['energy']

    def origin(self):
        return '%s-origin-%s' % (self.energyorigin, self.specie_id)

    def nsiname(self):
        if self.nsi_id:
            return self.nsi.name
        else:
            return None

    def auxillary(self):
        try:
            if self.aux:
                return 'true'
            else:
                return ''
        except AttributeError:
            return ''

    def nsiorigin(self):
        return '%s-origin-%s' % (self.nsioriginid, self.specie_id)

    def qns_xml(self):
        """Yield the XML for the state quantum numbers"""
        # remove "-origin" in order to retrieve also qns for state-origins
        try:
            sid = self.id.split('-')[0]
        except Exception:
            sid = self.id

        qns = MolecularQuantumNumbers.objects.filter(state=sid)
        case = qns[0].case
        caseNS = 'http://vamdc.org/xml/xsams/1.0/cases/%s' % case
        caseNSloc = '../../cases/%s.xsd' % case
        xml = []
        xml.append('<Case xsi:type="%s:Case" caseID="%s"'
                   ' xmlns:%s="%s" xsi:schemaLocation="%s %s">'
                   % (case, case, case, caseNS, caseNS, caseNSloc))
        xml.append('<%s:QNs>\n' % case)

        for qn in qns:
            if qn.attribute:
                # put quotes around the value of the attribute
                attr_name, attr_val = qn.attribute.split('=')
                qn.attribute = ' %s="%s"' % (attr_name, attr_val)
            else:
                qn.attribute = ''

            if qn.spinref:
                # add spinRef to attribute if it exists
                qn.attribute += ' nuclearSpinRef="%s"' % qn.spinref

            xml.append('<%s:%s%s>%s</%s:%s>\n' %
                       (case, qn.label, qn.attribute,
                        qn.value, case, qn.label))
        xml.append('</%s:QNs>\n' % case)
        xml.append('</Case>\n')
        return ''.join(xml)

    # associate qns_xml with the XML attribute of the States class
    # so that generators.py checkXML() works:

    def get_qns_xml(self):
        """
        Yield the XML for state quantum numbers, generated from the
        filter-table
        """

        try:
            qns = FILTER_DICT[self.specie_id][self.qntag]
        except Exception:
            if self.specie_id not in FILTER_DICT:
                FILTER_DICT[self.specie_id] = {}
            if self.qntag not in FILTER_DICT:
                where = models.Q(specie=self.specie) \
                        & models.Q(qntag=self.qntag)
                qns = QuantumNumbersFilter.objects.filter(where)
                FILTER_DICT[self.specie_id][self.qntag] = qns

        case = qns[0].case
        caseNS = 'http://vamdc.org/xml/xsams/1.0/cases/%s' % case
        caseNSloc = '../../cases/%s.xsd' % case
        xml = []
        xml.append('<Case xsi:type="%s:Case" caseID="%s"'
                   ' xmlns:%s="%s" xsi:schemaLocation="%s %s">'
                   % (case, case, case, caseNS, caseNS, caseNSloc))
        xml.append('<%s:QNs>\n' % case)

        for qn in qns:
            if qn.columnvalue:
                exec('value = self.qn%s' % qn.columnvalue)
                if qn.columnvaluefunc == 'half':
                    value -= 0.5

            elif qn.valuefloat is not None:
                value = qn.valuefloat
            elif qn.valuestring:
                value = qn.valuestring

            if qn.attribute:
                # put quotes around the value of the attribute
                attr_name, attr_val = qn.attribute.split('=')
                qn.attribute = ' %s="%s"' % (attr_name, attr_val)
            else:
                qn.attribute = ''

            if qn.spinref:
                # add spinRef to attribute if it exists
                qn.attribute += ' nuclearSpinRef="%s"' % qn.spinref

            xml.append('<%s:%s%s>%s</%s:%s>\n' %
                       (case, qn.label, qn.attribute, value, case, qn.label))
        xml.append('</%s:QNs>\n' % case)
        xml.append('</Case>\n')
        return ''.join(xml)

    XML = qns_xml

    def qns_dict(self):
        """ Yield the quantum numbers as a dictionary """
        qns = MolecularQuantumNumbers.objects.filter(state=self.id)
        dictqns = {}

        for qn in qns:
            dictqns.update({qn.label: qn.value})
        return dictqns


class StateOriginManager(models.Manager):
    def get_queryset(self):
        return super(StateOriginManager,
                     self).get_queryset().filter(id=models.F('energyorigin'))


class NSIStateOriginManager(models.Manager):
    def get_queryset(self):
        return super(NSIStateOriginManager,
                     self).get_queryset().filter(id=models.F('nsioriginid'))


class OriginStates(States):
    molecularspecie = models.ForeignKey(
            Species, db_column='EGY_E_ID', on_delete=models.DO_NOTHING)

    objects = StateOriginManager()
    nsi_objects = NSIStateOriginManager()

    class Meta:
        proxy = True

    def aux(self):
        return True

    def id_alias(self):
        return "%s-origin-%s" % (self.id, self.specie_id)


class AtomStates(models.Model):
    """
    This class contains the states of each specie.
    """
    id = models.IntegerField(primary_key=True, db_column='EGY_ID')
    specie = models.ForeignKey(
            Species, db_column='EGY_E_ID', on_delete=models.CASCADE)
    speciestag = models.IntegerField(db_column='EGY_E_Tag')
    dataset = models.ForeignKey(
            Datasets, db_column='EGY_DAT_ID', on_delete=models.CASCADE)
    energy = models.FloatField(null=True, db_column='EGY_Energy')
    uncertainty = models.FloatField(null=True, db_column='EGY_Uncertainty')
    energyorigin = models.IntegerField(db_column='EGY_EnergyOrigin_EGY_ID')
    mixingcoeff = models.FloatField(null=True, db_column='EGY_PMIX')
    block = models.IntegerField(db_column='EGY_IBLK')
    index = models.IntegerField(db_column='EGY_INDX')
    degeneracy = models.IntegerField(db_column='EGY_IDGN')
    nuclearstatisticalweight = models.IntegerField(
        db_column='EGY_NuclearStatisticalWeight')
    nuclearspinisomer = models.CharField(
        max_length=10, db_column='EGY_NuclearSpinIsomer')
    qntag = models.IntegerField(db_column='EGY_QN_Tag')
    qn1 = models.IntegerField(db_column='EGY_QN1')
    qn2 = models.IntegerField(db_column='EGY_QN2')
    qn3 = models.IntegerField(db_column='EGY_QN3')
    qn4 = models.IntegerField(db_column='EGY_QN4')
    qn5 = models.IntegerField(db_column='EGY_QN5')
    qn6 = models.IntegerField(db_column='EGY_QN6')
    user = models.CharField(max_length=40, db_column='EGY_User')  # obsolete
    timestamp = models.IntegerField(db_column='EGY_TIMESTAMP')

    objects = models.Manager()
    energy_origin = StateOriginManager()

    class Meta:
        db_table = u'Energies'

    def get_Components(self):
        """This is required in order to supply a Components property
        for the makeAtomsComponents tagmaker."""
        self.attach_atomic_qn()
        return self
    Components = property(get_Components)

    def attach_atomic_qn(self):
        """
        Attaches atomic states
        """

        qns = QuantumNumbersFilter.objects.filter(specie=self.specie)
        self.F = None
        for qn in qns:
            # if qn.label == 'L':
            #     self.L = qn.valuefloat
            # elif qn.label == 'S':
            #     self.S = qn.valuefloat
            if qn.columnvalue:
                exec('value = self.qn%s' % qn.columnvalue)
                if qn.columnvaluefunc == 'half':
                    value -= 0.5

            elif qn.valuefloat:
                value = qn.valuefloat
            elif qn.valuestring:
                value = qn.valuestring

            # convert floats to integer for some QNs
            if qn.label in ['L']:
                value = int(value)

            exec('self.%s = %s' % (qn.label, value))
        return self.J

    def auxillary(self):
        try:
            if self.aux:
                return 'True'
            else:
                return ''
        except AttributeError:
            return ''

    def id_alias(self):
        return "%s-origin-%s" % (self.id, self.specie_id)


class TransitionsCalc(models.Model):
    """
    This class contains the calculated transition frequencies (mysql-table
    Predictions).
    """
    id = models.IntegerField(primary_key=True, db_column='P_ID')
    specie = models.ForeignKey(
            Species, db_column='P_E_ID', on_delete=models.CASCADE)
    speciestag = models.IntegerField(db_column='P_E_Tag')
    frequency = models.FloatField(null=True, db_column='P_Frequency')
    frequencyexp = models.FloatField(null=True, db_column='P_Frequency_Exp')
    intensity = models.FloatField(null=True, db_column='P_Intensity')
    einsteina = models.FloatField(null=True, db_column='P_EinsteinA')
    smu2 = models.FloatField(null=True, db_column='P_Smu2')
    uncertainty = models.FloatField(null=True, db_column='P_Uncertainty')
    energylower = models.FloatField(null=True, db_column='P_Energy_Lower')
    energyupper = models.FloatField(null=True, db_column='P_Energy_Upper')
    qntag = models.IntegerField(db_column='P_QN_TAG')
    qnup1 = models.IntegerField(db_column='P_QN_Up_1')
    qnup2 = models.IntegerField(db_column='P_QN_Up_2')
    qnup3 = models.IntegerField(db_column='P_QN_Up_3')
    qnup4 = models.IntegerField(db_column='P_QN_Up_4')
    qnup5 = models.IntegerField(db_column='P_QN_Up_5')
    qnup6 = models.IntegerField(db_column='P_QN_Up_6')
    qnlow1 = models.IntegerField(db_column='P_QN_Low_1')
    qnlow2 = models.IntegerField(db_column='P_QN_Low_2')
    qnlow3 = models.IntegerField(db_column='P_QN_Low_3')
    qnlow4 = models.IntegerField(db_column='P_QN_Low_4')
    qnlow5 = models.IntegerField(db_column='P_QN_Low_5')
    qnlow6 = models.IntegerField(db_column='P_QN_Low_6')
    dummy = models.CharField(max_length=20, db_column='P_Dummy')
    unit = models.CharField(max_length=200, db_column='P_Unit')
    degreeoffreedom = models.IntegerField(db_column='P_Degree_Of_Freedom')
    upperstatedegeneracy = models.IntegerField(
            db_column='P_Upper_State_Degeneracy')
    originid = models.IntegerField(db_column='P_Origin_Id')
    hfsflag = models.IntegerField(db_column='P_HFS')
    userid = models.IntegerField(db_column='P_U_ID')
    dataset = models.ForeignKey(
            Datasets, db_column='P_DAT_ID', on_delete=models.CASCADE)
    qualityflag = models.IntegerField(db_column='P_Quality')
    archiveflag = models.IntegerField(db_column='P_Archive')
    timestamp = models.DateTimeField(db_column='P_TIMESTAMP')
    upperstateref = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='P_Up_EGY_ID',
            on_delete=models.DO_NOTHING)
    lowerstateref = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='P_Low_EGY_ID',
            on_delete=models.DO_NOTHING)

    upstate = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='P_Up_EGY_ID',
            on_delete=models.DO_NOTHING)
    lostate = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='P_Low_EGY_ID',
            on_delete=models.DO_NOTHING)
    # frequencyArray

    def __unicode__(self):
        return u'ID:%s Tag:%s Freq: %s' \
                % (self.id, self.speciestag, self.frequency)

    def specieid(self):
        return '%s-hyp%s' % (self.specie_id, self.hfsflag)

    def process_class(self):
        pclass = ['rota']
        if self.hfsflag > 0:
            pclass.append('hyp%d' % self.hfsflag)
        return pclass

    def attach_evaluation(self):
        """
        """
        self.qualities = []
        self.recommendations = []
        self.evalrefs = []
        evals = self.evaluation_set.all()
        for i in evals:
            self.qualities.append(i.quality)
            self.recommendations.append(i.recommended)
            self.evalrefs.append(i.source_id)
        return self.qualities

    def attach_exp_frequencies(self):
        """
        Create lists of frequencies, units, sources, ... for each transition.
        The calculated frequency is given anyway followed by experimental
        frequencies (db-table: Frequencies). In addition a unique list of
        methods for the experimental data is created and returned.

        Returns:
        - modified transitions (frequencies, ... attached as lists)
        - methods for experimental data

        """
        # Attach the calculated frequency first
        self.frequencies = [self.frequency]
        self.units = [self.unit]
        self.uncertainties = [self.uncertainty]
        self.refs = [""]
        self.methods = [self.dataset_id]
        self.evaluations = [self.attach_evaluation()]
        self.recommendations = [self.recommendations]
        self.evalrefs = [self.evalrefs]

        exptranss = TransitionsExp.objects.filter(specie=self.specie,
                                                  dataset__archiveflag=0,
                                                  qnup1=self.qnup1,
                                                  qnlow1=self.qnlow1,
                                                  qnup2=self.qnup2,
                                                  qnlow2=self.qnlow2,
                                                  qnup3=self.qnup3,
                                                  qnlow3=self.qnlow3,
                                                  qnup4=self.qnup4,
                                                  qnlow4=self.qnlow4,
                                                  qnup5=self.qnup5,
                                                  qnlow5=self.qnlow5,
                                                  qnup6=self.qnup6,
                                                  qnlow6=self.qnlow6)

        for exptrans in exptranss:
            self.frequencies.append(exptrans.frequency)
            self.units.append(exptrans.unit)
            self.uncertainties.append(exptrans.uncertainty)
            self.evaluations.append(exptrans.attach_evaluation())
            self.recommendations.append(exptrans.recommendations)
            self.evalrefs.append(exptrans.evalrefs)
            # get sources
            s = exptrans.sources.all().values_list('source', flat=True)
            self.refs.append(s)

            # if s.count()>0:
            #     method = "EXP" + "-".join(str(source) for source in s)
            #     self.methods.append(method)
            self.methods.append(exptrans.dataset_id)

        return self.frequencies

    def spfitstr(self):
        if self.frequencyexp:
            frequency = self.frequencyexp
            speciestag = -self.speciestag
        else:
            frequency = self.frequency
            speciestag = self.speciestag

        egy_lower = formatstring(self.energylower, '%10.4lf', '%10s')
        if egy_lower == '   -0.0000':
            egy_lower = '    0.0000'

        return '%s%s%s%s%s%3s%s%s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s'\
               % (formatstring(frequency, '%13.4lf', '%13s'),
                  formatstring(self.uncertainty, '%8.4lf', '%8s'),
                  formatstring(self.intensity, '%8.4lf', '%8s'),
                  formatstring(self.degreeoffreedom, '%2d', '%s'),
                  egy_lower,
                  format_degeneracy(self.upperstatedegeneracy),
                  formatstring(speciestag, '%7d', '%7s'),
                  formatstring(self.qntag, '%4d', '%4s'),
                  formatqn(self.qnup1),
                  formatqn(self.qnup2),
                  formatqn(self.qnup3),
                  formatqn(self.qnup4),
                  formatqn(self.qnup5),
                  formatqn(self.qnup6),
                  formatqn(self.qnlow1),
                  formatqn(self.qnlow2),
                  formatqn(self.qnlow3),
                  formatqn(self.qnlow4),
                  formatqn(self.qnlow5),
                  formatqn(self.qnlow6))

    class Meta:
        db_table = u'Predictions'


class RadiativeTransitions(models.Model):
    """
    This class contains the calculated transition frequencies (mysql-table
    Predictions).
    """
    id = models.IntegerField(
            primary_key=True, db_column='RadiativeTransitionID')
    specie = models.ForeignKey(
            Species, db_column='SpeciesID', on_delete=models.CASCADE)
    speciestag = models.IntegerField(db_column='SpeciesTag')
    frequency = models.FloatField(null=True, db_column='FrequencyValue')
    intensity = models.FloatField(null=True, db_column='IdealisedIntensity')
    einsteina = models.FloatField(null=True, db_column='EinsteinA')
    # smu2 =  models.FloatField(null=True, db_column='P_Smu2')
    uncertainty = models.FloatField(
            null=True, db_column='EnergyWavelengthAccuracy')
    energylower = models.FloatField(
            null=True, db_column='LowerStateEnergyValue')
    # energyupper =  models.FloatField(null=True, db_column='P_Energy_Upper')
    qntag = models.IntegerField(db_column='CaseQN')
    qnup1 = models.IntegerField(db_column='QN_Up_1')
    qnup2 = models.IntegerField(db_column='QN_Up_2')
    qnup3 = models.IntegerField(db_column='QN_Up_3')
    qnup4 = models.IntegerField(db_column='QN_Up_4')
    qnup5 = models.IntegerField(db_column='QN_Up_5')
    qnup6 = models.IntegerField(db_column='QN_Up_6')
    qnlow1 = models.IntegerField(db_column='QN_Low_1')
    qnlow2 = models.IntegerField(db_column='QN_Low_2')
    qnlow3 = models.IntegerField(db_column='QN_Low_3')
    qnlow4 = models.IntegerField(db_column='QN_Low_4')
    qnlow5 = models.IntegerField(db_column='QN_Low_5')
    qnlow6 = models.IntegerField(db_column='QN_Low_6')
    unit = models.CharField(max_length=200, db_column='FrequencyUnit')
    degreeoffreedom = models.IntegerField(db_column='Degree_Of_Freedom')
    upperstatedegeneracy = models.IntegerField(
        db_column='UpperStateNuclearStatisticalWeight')
    originid = models.IntegerField(db_column='Resource')
    hfsflag = models.IntegerField(db_column='hfsflag')
    # userid = models.IntegerField(db_column='P_U_ID')
    dataset = models.ForeignKey(
            Datasets, db_column='DAT_ID', on_delete=models.CASCADE)
    # qualityflag = models.IntegerField(db_column='P_Quality')
    # archiveflag = models.IntegerField(db_column='P_Archive')
    timestamp = models.DateTimeField(db_column='Createdate')
    frequencies = models.CharField(db_column='FrequencyList')
    uncertainties = models.CharField(db_column='UncertaintyList')
    methods = models.CharField(db_column='MethodList')
    references = models.CharField(db_column='ReferenceList')
    frequencymethod = models.IntegerField(db_column='FrequencyMethodRef')
    processclass = models.CharField(max_length=100, db_column='ProcessClass')

    upperstateref = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='UpperStateRef',
            on_delete=models.DO_NOTHING)
    lowerstateref = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='LowerStateRef',
            on_delete=models.DO_NOTHING)

    upstate = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='UpperStateRef',
            on_delete=models.DO_NOTHING)
    lostate = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='LowerStateRef',
            on_delete=models.DO_NOTHING)

    def line_strength(self):
        if self.intensity is not None:
            return format(
                    np.power(10.0, self.intensity) / (2.99792458e18), '.5g')
        else:
            return 0.0

    def __str__(self):
        return u'ID:%s Tag:%s Freq: %s' \
                % (self.id, self.speciestag, self.frequency)

    def specieid(self):
        return '%s-hyp%s' % (self.specie_id, self.hfsflag)

    def spfitstr(self, print_einsteina=False):
        if self.frequencymethod == 4:
            speciestag = -self.speciestag
        else:
            speciestag = self.speciestag

        egy_lower = formatstring(self.energylower, '%10.4lf', '%10s')
        if egy_lower == '   -0.0000':
            egy_lower = '    0.0000'

        if print_einsteina:
            intensity = formatstring(np.log10(self.einsteina), '%8.4lf', '%8s')
        else:
            intensity = formatstring(self.intensity, '%8.4lf', '%8s')
        return '%s%s%s%s%s%3s%s%s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s'\
               % (formatstring(self.frequency, '%13.4lf', '%13s'),
                  formatstring(self.uncertainty, '%8.4lf', '%8s'),
                  intensity,
                  formatstring(self.degreeoffreedom, '%2d', '%s'),
                  egy_lower,
                  format_degeneracy(self.upperstatedegeneracy),
                  formatstring(speciestag, '%7d', '%7s'),
                  formatstring(self.qntag, '%4d', '%4s'),
                  formatqn(self.qnup1),
                  formatqn(self.qnup2),
                  formatqn(self.qnup3),
                  formatqn(self.qnup4),
                  formatqn(self.qnup5),
                  formatqn(self.qnup6),
                  formatqn(self.qnlow1),
                  formatqn(self.qnlow2),
                  formatqn(self.qnlow3),
                  formatqn(self.qnlow4),
                  formatqn(self.qnlow5),
                  formatqn(self.qnlow6))

    class Meta:
        db_table = u'RadiativeTransitions'


class RadiativeTransitionsT(models.Model):
    """
    This class contains the calculated transition frequencies (mysql-view
    RadiativeTransitionsT) with temperature dependend intensities.
    """
    id = models.IntegerField(
            primary_key=True, db_column='RadiativeTransitionID')
    specie = models.ForeignKey(
            Species, db_column='SpeciesID', on_delete=models.CASCADE)
    speciestag = models.IntegerField(db_column='SpeciesTag')
    frequency = models.FloatField(null=True, db_column='FrequencyValue')
    intensity = models.FloatField(
            null=True, db_column='IdealisedIntensityT')
    einsteina = models.FloatField(null=True, db_column='EinsteinA')
    # smu2 =  models.FloatField(null=True, db_column='P_Smu2')
    uncertainty = models.FloatField(
            null=True, db_column='EnergyWavelengthAccuracy')
    energylower = models.FloatField(
            null=True, db_column='LowerStateEnergyValue')
    # energyupper =  models.FloatField(null=True, db_column='P_Energy_Upper')
    qntag = models.IntegerField(db_column='CaseQN')
    qnup1 = models.IntegerField(db_column='QN_Up_1')
    qnup2 = models.IntegerField(db_column='QN_Up_2')
    qnup3 = models.IntegerField(db_column='QN_Up_3')
    qnup4 = models.IntegerField(db_column='QN_Up_4')
    qnup5 = models.IntegerField(db_column='QN_Up_5')
    qnup6 = models.IntegerField(db_column='QN_Up_6')
    qnlow1 = models.IntegerField(db_column='QN_Low_1')
    qnlow2 = models.IntegerField(db_column='QN_Low_2')
    qnlow3 = models.IntegerField(db_column='QN_Low_3')
    qnlow4 = models.IntegerField(db_column='QN_Low_4')
    qnlow5 = models.IntegerField(db_column='QN_Low_5')
    qnlow6 = models.IntegerField(db_column='QN_Low_6')
    unit = models.CharField(max_length=200, db_column='FrequencyUnit')
    degreeoffreedom = models.IntegerField(db_column='Degree_Of_Freedom')
    upperstatedegeneracy = models.IntegerField(
        db_column='UpperStateNuclearStatisticalWeight')
    originid = models.IntegerField(db_column='Resource')
    hfsflag = models.IntegerField(db_column='hfsflag')
    # userid = models.IntegerField(db_column='P_U_ID')
    dataset = models.ForeignKey(
            Datasets, db_column='DAT_ID', on_delete=models.CASCADE)
    # qualityflag = models.IntegerField(db_column='P_Quality')
    # archiveflag = models.IntegerField(db_column='P_Archive')
    timestamp = models.DateTimeField(db_column='Createdate')
    temperature = models.FloatField(db_column='Temperature')
    partitionfunc300 = models.FloatField(db_column='Partitionfunction300K')
    partitionfuncT = models.FloatField(db_column='PartitionfunctionT')
    frequencies = models.CharField(db_column='FrequencyList')
    uncertainties = models.CharField(db_column='UncertaintyList')
    methods = models.CharField(db_column='MethodList')
    references = models.CharField(db_column='ReferenceList')
    frequencymethod = models.IntegerField(db_column='FrequencyMethodRef')
    processclass = models.CharField(max_length=100, db_column='ProcessClass')

    upperstateref = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='UpperStateRef',
            on_delete=models.DO_NOTHING)
    lowerstateref = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='LowerStateRef',
            on_delete=models.DO_NOTHING)
    upstate = models.ForeignKey(
            States,
            related_name='upperstate',
            db_column='UpperStateRef',
            on_delete=models.DO_NOTHING)
    lostate = models.ForeignKey(
            States,
            related_name='lowerstate',
            db_column='LowerStateRef',
            on_delete=models.DO_NOTHING)

    def line_strength(self):
        return format(np.power(10.0, self.intensity) / (2.99792458e18), '.5g')
    # frequencyArray

    def __str__(self):
        return u'ID:%s Tag:%s Freq: %s' \
                % (self.id, self.speciestag, self.frequency)

    def specieid(self):
        return '%s-hyp%s' % (self.specie_id, self.hfsflag)

    def spfitstr(self, print_einsteina=False):
        if self.frequencymethod == 4:
            speciestag = -self.speciestag
        else:
            speciestag = self.speciestag

        egy_lower = formatstring(self.energylower, '%10.4lf', '%10s')
        if egy_lower == '   -0.0000':
            egy_lower = '    0.0000'

        if print_einsteina:
            intensity = formatstring(np.log10(self.einsteina), '%8.4lf', '%8s')
        else:
            intensity = formatstring(self.intensity, '%8.4lf', '%8s')

        return '%s%s%s%s%s%3s%s%s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s%2s'\
               % (formatstring(self.frequency, '%13.4lf', '%13s'),
                  formatstring(self.uncertainty, '%8.4lf', '%8s'),
                  intensity,
                  formatstring(self.degreeoffreedom, '%2d', '%s'),
                  egy_lower,
                  format_degeneracy(self.upperstatedegeneracy),
                  formatstring(speciestag, '%7d', '%7s'),
                  formatstring(self.qntag, '%4d', '%4s'),
                  formatqn(self.qnup1),
                  formatqn(self.qnup2),
                  formatqn(self.qnup3),
                  formatqn(self.qnup4),
                  formatqn(self.qnup5),
                  formatqn(self.qnup6),
                  formatqn(self.qnlow1),
                  formatqn(self.qnlow2),
                  formatqn(self.qnlow3),
                  formatqn(self.qnlow4),
                  formatqn(self.qnlow5),
                  formatqn(self.qnlow6))

    class Meta:
        db_table = u'RadiativeTransitionsT'


class Sources(models.Model):
    """
    This class contains references
    """
    id = models.IntegerField(primary_key=True, db_column='R_ID')
    authors = models.CharField(
            max_length=500, db_column='R_Authors', blank=True)
    category = models.CharField(
            max_length=100, db_column='R_Category', blank=True)
    name = models.CharField(
            max_length=200, db_column='R_SourceName', blank=True)
    title = models.CharField(max_length=200, db_column='R_Title', blank=True)
    year = models.IntegerField(null=True, db_column='R_Year', blank=True)
    vol = models.CharField(max_length=20, db_column='R_Volume', blank=True)
    doi = models.CharField(max_length=50, db_column='R_DOI', blank=True)
    pageBegin = models.CharField(
            max_length=10, db_column='R_PageBegin', blank=True)
    pageEnd = models.CharField(
            max_length=10, db_column='R_PageEnd', blank=True)
    uri = models.CharField(max_length=100, db_column='R_URI', blank=True)
    publisher = models.CharField(
            max_length=300, db_column='R_Publisher', blank=True)
    city = models.CharField(max_length=80, db_column='R_City', blank=True)
    editors = models.CharField(
            max_length=300, db_column='R_Editors', blank=True)
    productionDate = models.DateField(
        max_length=12, db_column='R_ProductionDate', blank=True)
    version = models.CharField(
            max_length=20, db_column='R_Version', blank=True)
    url = models.CharField(max_length=200, db_column='R_URL', blank=True)
    comments = models.CharField(
            max_length=100, db_column='R_Comments', blank=True)

    class Meta:
        db_table = u'ReferenceBib'

    def getAuthorList(self):
        try:
            return [name.replace("{", "").replace("}", "")
                    for name in self.authors.split("},{")]
        except Exception:
            return None


class Parameter (models.Model):
    id = models.IntegerField(primary_key=True, db_column='PAR_ID')
    specie = models.ForeignKey(
            Species, db_column='PAR_E_ID', on_delete=models.CASCADE)
    speciestag = models.IntegerField(db_column='PAR_M_TAG')
    parameter = models.CharField(max_length=100, db_column='PAR_PARAMETER')
    value = models.CharField(max_length=100, db_column='PAR_VALUE')
    unit = models.CharField(max_length=7, db_column='PAR_UNIT')
    type = models.CharField(max_length=30, db_column='PAR_Type')
    rId = models.ForeignKey(
            Sources, db_column='PAR_R_ID', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = u'Parameter'

    def parameter_html(self):
        u_score = self.parameter.find('_')
        if u_score < 0:
            return self.parameter
        else:
            return self.parameter.replace(
                    self.parameter[u_score:u_score+2],
                    '<sub>'+self.parameter[u_score+1:u_score+2]+'</sub>')


class TransitionsExp(models.Model):
    """
    This class contains the experimental transition frequencies (mysql-table
    Frequencies).
    """
    id = models.IntegerField(primary_key=True, db_column='F_ID')
    specie = models.ForeignKey(
            Species, db_column='F_E_ID', on_delete=models.CASCADE)
    vid = models.IntegerField(db_column='F_V_ID')  # obsolete
    frequency = models.FloatField(null=True, db_column='F_Frequency')
    uncertainty = models.FloatField(null=True, db_column='F_Error')
    weight = models.FloatField(null=True, db_column='F_WT')
    unit = models.CharField(max_length=10, db_column='F_Unit')
    qnup1 = models.IntegerField(db_column='F_QN_Up_1')
    qnup2 = models.IntegerField(db_column='F_QN_Up_2')
    qnup3 = models.IntegerField(db_column='F_QN_Up_3')
    qnup4 = models.IntegerField(db_column='F_QN_Up_4')
    qnup5 = models.IntegerField(db_column='F_QN_Up_5')
    qnup6 = models.IntegerField(db_column='F_QN_Up_6')
    qnlow1 = models.IntegerField(db_column='F_QN_Low_1')
    qnlow2 = models.IntegerField(db_column='F_QN_Low_2')
    qnlow3 = models.IntegerField(db_column='F_QN_Low_3')
    qnlow4 = models.IntegerField(db_column='F_QN_Low_4')
    qnlow5 = models.IntegerField(db_column='F_QN_Low_5')
    qnlow6 = models.IntegerField(db_column='F_QN_Low_6')
    comment = models.TextField(db_column='F_Comment')
    rating = models.IntegerField(db_column='F_Rating')
    userid = models.IntegerField(db_column='F_U_ID')
    papid = models.IntegerField(db_column='F_PAP_ID')  # obsolete
    dataset = models.ForeignKey(
            Datasets, db_column='F_DAT_ID', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
            db_column='F_TIMESTAMP')
    sources = models.ManyToManyField(Sources, through='SourcesIDRefs')

    class Meta:
        db_table = u'Frequencies'

    def spfitstr(self):
        """
        Renders the current transition in spfit's output format
        12I3, freeform: QN, FREQ, ERR, WT
        """
        qnupstr = ""
        qnlowstr = ""
        emptystr = ""
        for qn in [self.qnup1, self.qnup2, self.qnup3,
                   self.qnup4, self.qnup5, self.qnup6]:
            if qn is not None:
                qnupstr += '%3d' % qn
            else:
                emptystr += '   '
        for qn in [self.qnlow1, self.qnlow2, self.qnlow3,
                   self.qnlow4, self.qnlow5, self.qnlow6]:
            if qn is not None:
                qnlowstr += '%3d' % qn
            else:
                emptystr += '   '

        return '%s'\
               '%s %s %s  '\
               '%s'\
               % (qnupstr+qnlowstr+emptystr,
                  '%16.4lf' % self.frequency if self.frequency else "",
                  '%10.4lf' % self.uncertainty if self.uncertainty else "",
                  '%8.4lf' % self.weight if self.weight else "",
                  self.comment)

    def __unicode__(self):
        return self.spfitstr()

    def attach_evaluation(self):
        """
        """
        self.qualities = []
        self.recommendations = []
        self.evalrefs = []
        evals = self.evaluation_set.all()
        for i in evals:
            self.qualities.append(i.quality)
            self.recommendations.append(i.recommended)
            self.evalrefs.append(i.source_id)
        return self.qualities


class SourcesIDRefs(models.Model):
    """
    This class maps references to classes: species, datasets, frequency
    """
    id = models.AutoField(primary_key=True, db_column='RL_ID')
    source = models.ForeignKey(
            Sources,
            null=True,
            db_column='RL_R_ID',
            on_delete=models.DO_NOTHING)
    specie = models.ForeignKey(
            Species,
            null=True,
            db_column='RL_E_ID',
            on_delete=models.DO_NOTHING)
    dataset = models.ForeignKey(
            Datasets,
            null=True,
            db_column='RL_DAT_ID',
            blank=True,
            on_delete=models.DO_NOTHING)
    transitionexp = models.ForeignKey(
            TransitionsExp,
            null=True,
            db_column='RL_F_ID',
            related_name='sources',
            blank=True,
            on_delete=models.DO_NOTHING)
    parameter = models.ForeignKey(
            Parameter,
            null=True,
            db_column='RL_F_ID',
            blank=True,
            on_delete=models.DO_NOTHING)

    class Meta:
        db_table = u'ReferenceList'


class Methods (models.Model):
    id = models.IntegerField(primary_key=True, db_column='ME_ID')
    ref = models.CharField(max_length=10, db_column='ME_Ref')
    functionref = models.IntegerField(db_column='ME_FunctionRef')
    category = models.CharField(max_length=30, db_column='ME_Category')
    description = models.CharField(max_length=500, db_column='ME_Description')

    class Meta:
        db_table = u'Methods'


class MolecularQuantumNumbers(models.Model):
    """
    This class is based on the mysql-view 'V_MolstateQN' and contains
    the transformed quantum numbers of a state (spcat->XSAMS)
    """
    id = models.IntegerField(primary_key=True, db_column='Id')
    state = models.ForeignKey(
            States,
            related_name='quantumnumbers',
            db_column='StateID',
            on_delete=models.CASCADE)
    case = models.CharField(max_length=10, db_column='Case')
    label = models.CharField(max_length=50, db_column='Label')
    value = models.CharField(max_length=100, db_column='Value')
    spinref = models.CharField(max_length=100, db_column='SpinRef')
    attribute = models.CharField(max_length=100, db_column='Attribute')

    class Meta:
        db_table = 'V_MolstateQN'
        managed = False


class QuantumNumbersFilter(models.Model):
    """
    This table (StateQNXsams) is used to map spcat's QuantumNumbers
    to XSAMS Quantum numbers (case description)
    """
    id = models.IntegerField(primary_key=True, db_column='SQN_ID')
    specie = models.ForeignKey(
            Species, db_column='SQN_E_ID', on_delete=models.CASCADE)
    qntag = models.IntegerField(db_column='SQN_QN_Tag')
    qn1 = models.IntegerField(db_column='SQN_QN1')
    qn2 = models.IntegerField(db_column='SQN_QN2')
    qn3 = models.IntegerField(db_column='SQN_QN3')
    qn4 = models.IntegerField(db_column='SQN_QN4')
    qn5 = models.IntegerField(db_column='SQN_QN5')
    qn6 = models.IntegerField(db_column='SQN_QN6')
    case = models.CharField(max_length=20, db_column='SQN_Case')
    label = models.CharField(max_length=100, db_column='SQN_Label')
    slaplabel = models.CharField(max_length=100, db_column='SQN_SLAP_Label')
    valuefloat = models.FloatField(db_column='SQN_ValueFloat')
    valuestring = models.CharField(max_length=100, db_column='SQN_ValueString')
    columnvalue = models.IntegerField(db_column='SQN_ColumnValue')
    columnvaluefunc = models.CharField(
        max_length=10, db_column='SQN_ColumnValueFunction')
    spinref = models.CharField(max_length=10, db_column='SQN_SpinRef')
    attribute = models.CharField(max_length=20, db_column='SQN_Attribute')
    order = models.IntegerField(db_column='SQN_Order')
    comment = models.TextField(db_column='SQN_Comment')

    class Meta:
        db_table = 'StateQNXsams'


class BondArray(models.Model):
    """
    This class contains the bonds of each specie. One bond per object.
    atom1 and atom2 correspond to atomid of the AtomArray - class.
    """
    id = models.IntegerField(primary_key=True, db_column='BA_ID')
    inchikey = models.CharField(max_length=100, db_column='BA_InchiKey')
    atom1 = models.CharField(max_length=10, db_column='BA_AtomId1')
    atom2 = models.CharField(max_length=10, db_column='BA_AtomId2')
    order = models.CharField(max_length=10, db_column='BA_Order')
    specie = models.ForeignKey(
            Molecules, db_column='BA_E_ID', on_delete=models.CASCADE)

    class Meta:
        db_table = u'BondArray'


class AtomArray(models.Model):
    """
    This class contains the atoms of each specie. One atom per object.
    atomid is used in BondArray to identify atoms.
    """
    id = models.IntegerField(primary_key=True, db_column='AA_ID')
    inchikey = models.CharField(max_length=100, db_column='AA_InchiKey')
    atomid = models.CharField(max_length=10, db_column='AA_AtomId')
    elementtype = models.CharField(max_length=5, db_column='AA_ElementType')
    isotopenumber = models.IntegerField(db_column='AA_IsotopeNumber')
    formalcharge = models.CharField(max_length=5, db_column='AA_FormalCharge')
    specie = models.ForeignKey(
            Species, db_column='AA_E_ID', on_delete=models.CASCADE)

    class Meta:
        db_table = u'AtomArray'


class Evaluation(models.Model):
    """
    This class contains recommendations and evaluation information for specific
    transitions.  One transition (ether experimental or calculated) is
    evaluated. The entity is specified in source.
    """
    id = models.IntegerField(primary_key=True, db_column='EVA_ID')
    specie = models.ForeignKey(
            Species, db_column='EVA_E_ID', on_delete=models.CASCADE)
    exptransition = models.ForeignKey(
            TransitionsExp, db_column='EVA_F_ID', on_delete=models.CASCADE)
    calctransition = models.ForeignKey(
            TransitionsCalc, db_column='EVA_P_ID', on_delete=models.CASCADE)
    recommended = models.BooleanField(db_column='EVA_Recommended')
    quality = models.CharField(max_length=45, db_column='EVA_Quality')
    source = models.ForeignKey(
            Sources, db_column='EVA_R_ID', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = u'Evaluation'


class Partitionfunctions(models.Model):
    """
    This class contains partition function (mysql-table: Partitionfunctions)
    for each specie.
    """
    id = models.AutoField(primary_key=True, db_column='PF_ID')
    molecule = models.ForeignKey(
            Molecules,
            db_column='PF_M_ID',
            blank=True,
            null=True,
            on_delete=models.DO_NOTHING)
    specie = models.ForeignKey(
            Species,
            db_column='PF_E_ID',
            on_delete=models.DO_NOTHING)
    dataset = models.ForeignKey(
            Datasets,
            db_column='PF_DAT_ID',
            blank=True,
            null=True,
            on_delete=models.DO_NOTHING)
    nsi = models.ForeignKey(
            NuclearSpinIsomers,
            db_column='PF_NSI_ID',
            blank=True,
            null=True,
            on_delete=models.DO_NOTHING)
    temperature = models.FloatField(db_column='PF_Temperature')
    partitionfunc = models.FloatField(db_column='PF_Partitionfunction')
    state = models.CharField(max_length=100, db_column='PF_State')
    comment = models.CharField(max_length=150, db_column='PF_Comment')

    class Meta:
        db_table = u'Partitionfunctions'


class PartitionfunctionsDetailed(models.Model):
    """
    This class contains partition function (mysql-table: Partitionfunctions)
    for each specie which have been calculated based on the state energy
    listing and include contributions from other vibrational states (other
    specie).
    """
    id = models.AutoField(primary_key=True, db_column='PFD_ID')
    specie = models.ForeignKey(
            Species, db_column='PFD_E_ID', on_delete=models.DO_NOTHING)
    inchikey = models.CharField(
        max_length=30, db_column='PFD_Inchikey', blank=True, null=True)
    state = models.CharField(max_length=100, db_column='PFD_State')
    loweststateenergy = models.FloatField(db_column='PFD_LowestStateEnergy')
    nsi = models.ForeignKey(
            NuclearSpinIsomers,
            db_column='PFD_NSI',
            blank=True,
            null=True,
            on_delete=models.DO_NOTHING)
    temperature = models.FloatField(db_column='PFD_Temperature')
    partitionfunc = models.FloatField(db_column='PFD_Partitionfunction')
    comment = models.CharField(max_length=150, db_column='PFD_Comment')
    createdate = models.DateTimeField(db_column='PFD_Createdate')
    changedate = models.DateTimeField(db_column='PFD_Changedate')

    class Meta:
        db_table = u'PartitionFunctionsDetailed'

    def __unicode__(self):
        return "%6d %20s %9.3lf %20.6lf" \
                % (self.specie.id,
                   self.state,
                   self.temperature,
                   self.partitionfunc)


class Method:
    """
    This class wraps the sources for each specie (like a header).
    """

    def __init__(self, id, speciesid, category, description, sourcesref):

        self.id = id
        self.speciesid = speciesid
        self.category = category
        self.description = description
        self.sourcesref = sourcesref


class Files (models.Model):
    id = models.IntegerField(primary_key=True, db_column='FIL_ID')
    specie = models.ForeignKey(
            Species, db_column='FIL_E_ID', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50, db_column='FIL_Name')
    type = models.CharField(max_length=10, db_column='FIL_Type')
    asciifile = models.TextField(db_column='FIL_ASCIIFILE')
    comment = models.TextField(db_column='FIL_Comment')
    createdate = models.DateField(db_column='FIL_Createdate')

    class Meta:
        db_table = u'Files'
