from django.db import models
from django.contrib.postgres.fields import IntegerRangeField


class Batting(models.Model):

    player_name = models.CharField(max_length=300)
    span = IntegerRangeField()
    Mat = models.IntegerField(null=True, blank=True)
    Inns = models.IntegerField(null=True, blank=True)
    Runs = models.IntegerField(null=True, blank=True)
    HS = models.CharField(max_length=4, null=True, blank=True)
    Ave = models.FloatField(null=True, blank=True)
    BF = models.IntegerField(null=True, blank=True)
    SR = models.FloatField(null=True, blank=True)
    Cent = models.IntegerField(null=True, blank=True)
    half_Cent = models.IntegerField(null=True, blank=True)
    duck = models.IntegerField(null=True, blank=True)
    fours = models.IntegerField(null=True, blank=True)
    sixes = models.IntegerField(null=True, blank=True)


class Bowling(models.Model):
    player_name = models.CharField(max_length=300)
    span = IntegerRangeField()
    Mat = models.IntegerField(null=True, blank=True)
    Inns = models.IntegerField(null=True, blank=True)
    Overs = models.FloatField(null=True, blank=True)
    Mdns = models.IntegerField(null=True, blank=True)
    Runs = models.IntegerField(null=True, blank=True)
    Wkts = models.IntegerField(null=True, blank=True)
    BBI = models.CharField(max_length=10, null=True, blank=True)
    Ave = models.FloatField(null=True, blank=True)
    Econ = models.FloatField(null=True, blank=True)
    SR = models.FloatField(null=True, blank=True)
    fours = models.IntegerField(null=True, blank=True)
    fives = models.IntegerField(null=True, blank=True)


class Fielding(models.Model):
    player_name = models.CharField(max_length=300)
    span = IntegerRangeField()
    Mat = models.IntegerField(null=True, blank=True)
    Inns = models.IntegerField(null=True, blank=True)
    Dis = models.IntegerField(null=True, blank=True)
    Ct = models.IntegerField(null=True, blank=True)
    St = models.IntegerField(null=True, blank=True)
    Ct_Wk = models.IntegerField(null=True, blank=True)
    Ct_Fi = models.IntegerField(null=True, blank=True)
    MD_total = models.IntegerField(null=True, blank=True)
    MD_Ct = models.IntegerField(null=True, blank=True)
    MD_St = models.IntegerField(null=True, blank=True)
    DPI = models.FloatField(null=True, blank=True)

# Create your models here.
