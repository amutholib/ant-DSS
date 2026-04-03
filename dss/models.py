from django.db import models

# Create your models here.

class SateliteAnomaly(models.Model):
    sa_id = models.AutoField(primary_key=True)
    spacecraftname = models.CharField(max_length=50, blank=True, null=True)
    internationalnumber = models.CharField(max_length=50, blank=True, null=True)
    eventdate = models.DateTimeField(blank=True, null=True)
    event = models.CharField(max_length=128, blank=True, null=True)
    capacitylost = models.FloatField(blank=True, null=True)
    lifelost = models.FloatField(blank=True, null=True)
    capabilitylost = models.FloatField(blank=True, null=True)
    age = models.FloatField(blank=True, null=True)
    designlife = models.FloatField(blank=True, null=True)
    bustype = models.CharField(max_length=50, blank=True, null=True)
    netinsuranceloss = models.FloatField(blank=True, null=True)
    insuranceloss = models.FloatField(blank=True, null=True)
    primemanufacturer = models.CharField(max_length=128, blank=True, null=True)
    spacecraftowner = models.CharField(max_length=128, blank=True, null=True)
    spacecraftoperator = models.CharField(max_length=128, blank=True, null=True)
    launchdate = models.DateTimeField(blank=True, null=True)
    vehiclelongname = models.CharField(max_length=50, blank=True, null=True)
    orbitcategory = models.CharField(max_length=50, blank=True, null=True)
    missionprimary = models.CharField(max_length=50, blank=True, null=True)
    massatlaunch = models.FloatField(blank=True, null=True)
    combinedcostatnew = models.FloatField(blank=True, null=True)
    spacecraftcostatnew = models.FloatField(blank=True, null=True)
    launchcost = models.FloatField(blank=True, null=True)
    totallaunchcost = models.FloatField(blank=True, null=True)
    eventremarks = models.TextField(blank=True, null=True)
    capabilitylostnotes = models.TextField(blank=True, null=True)
    insurancelossnotes = models.TextField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'satelite_anomaly'


class DSSCore(models.Model):
    c_id = models.AutoField(primary_key=True)
    bustype = models.CharField(max_length=100, blank=True, null=True)
    orbitcategory = models.CharField(max_length=100, blank=True, null=True)
    missionprimary = models.CharField(max_length=100, blank=True, null=True)
    genai = models.CharField(max_length=100, blank=True, null=True)
    incident_overview = models.TextField(blank=True, null=True)
    reliability_insight = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dss_core'

class VCountAltitude(models.Model):
    total_altitude = models.IntegerField()

    class Meta:
        managed = False  # No migrations will be created for this model
        db_table = 'v_count_altitude'  # Name of the view in the database


class VCountDocking(models.Model):
    total_docking = models.IntegerField()
    dummy_id = models.AutoField(primary_key=True)  # Add a dummy primary key

    class Meta:
        managed = False  # No migrations will be created for this model
        db_table = 'v_count_docking'  # Name of the view in the database
