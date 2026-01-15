from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from psycopg2.extras import NumericRange

import os
import re
import pandas as pd
import numpy as np

from core.models import Batting, Bowling, Fielding
def parse_span(span_str):
    if not span_str:
        return None
    start, end = span_str.split("-")
    return NumericRange(int(start), int(end), bounds="[]")


def parse_md(md_str):
    if not md_str:
        return None, None, None

    total_match = re.match(r"(\d+)", md_str)
    ct_match = re.search(r"(\d+)ct", md_str)
    st_match = re.search(r"(\d+)st", md_str)

    md_total = int(total_match.group(1)) if total_match else None
    md_ct = int(ct_match.group(1)) if ct_match else None
    md_st = int(st_match.group(1)) if st_match else None

    return md_total, md_ct, md_st

def load_fielding():

    df = pd.read_csv(
        "C:\\Users\\kunwar_fix\\Desktop\\Python\\NLP to SQL\\data\\Fielding_cleaned_v2.csv",
        index_col=0,
        na_values=["-", "NaN", "null", ""]
    )

    df.rename(columns={
        "Player": "player_name",
        "Span": "span",
        "Mat": "Mat",
        "Inns": "Inns",
        "Dis": "Dis",
        "Ct": "Ct",
        "St": "St",
        "Ct Wk": "Ct_Wk",
        "Ct Fi": "Ct_Fi",
        "MD": "MD",
        "D/I": "DPI",
    }, inplace=True)

    df = df.replace({np.nan: None})

    objs = []

    for row in df.itertuples(index=False):
        parsed_span = parse_span(row.span)
        md_total, md_ct, md_st = parse_md(row.MD)

        objs.append(
            Fielding(
                player_name=row.player_name,
                span=parsed_span,
                Mat=row.Mat,
                Inns=row.Inns,
                Dis=row.Dis,
                Ct=row.Ct,
                St=row.St,
                Ct_Wk=row.Ct_Wk,
                Ct_Fi=row.Ct_Fi,
                MD_total=md_total,
                MD_Ct=md_ct,
                MD_St=md_st,
                DPI=row.DPI
            )
        )

    Fielding.objects.bulk_create(objs, batch_size=1000)

def load_batting():

    df = pd.read_csv(
        "C:\\Users\\kunwar_fix\\Desktop\\Python\\NLP to SQL\\data\\Batting_cleaned_v2.csv",
        index_col=0,
        na_values=["-", "NaN", "null", ""]
    )

    df.rename(columns={
        "Player": "player_name",
        "Span": "span",
        "Mat": "Mat",
        "Inns": "Inns",
        "Runs": "Runs",
        "HS": "HS",
        "Ave": "Ave",
        "BF": "BF",
        "SR": "SR",
        "100": "Cent",
        "50": "half_Cent",
        "0": "duck",
        "4s": "fours",
        "6s": "sixes",
    }, inplace=True)

    df = df.replace({np.nan: None})

    objs = []

    for row in df.itertuples(index=False):
        objs.append(
            Batting(
                player_name=row.player_name,
                span=parse_span(row.span),
                Mat=row.Mat,
                Inns=row.Inns,
                Runs=row.Runs,
                HS=row.HS,
                Ave=row.Ave,
                BF=row.BF,
                SR=row.SR,
                Cent=row.Cent,
                half_Cent=row.half_Cent,
                duck=row.duck,
                fours=row.fours,
                sixes=row.sixes
            )
        )

    Batting.objects.bulk_create(objs, batch_size=1000)

def load_bowling():

    df = pd.read_csv(
        "C:\\Users\\kunwar_fix\\Desktop\Python\\NLP to SQL\\data\\Bowling_cleaned_v2.csv",
        index_col=0,
        na_values=["-", "NaN", "null", ""]
    )

    df.rename(columns={
        "Player": "player_name",
        "Span": "span",
        "Mat": "Mat",
        "Inns": "Inns",
        "Overs": "Overs",
        "Mdns": "Mdns",
        "Runs": "Runs",
        "Wkts": "Wkts",
        "BBI": "BBI",
        "Ave": "Ave",
        "Econ": "Econ",
        "SR": "SR",
        "4": "fours",
        "5": "fives",
    }, inplace=True)

    df = df.replace({np.nan: None})

    objs = []

    for row in df.itertuples(index=False):
        objs.append(
            Bowling(
                player_name=row.player_name,
                span=parse_span(row.span),
                Mat=row.Mat,
                Inns=row.Inns,
                Overs=row.Overs,
                Mdns=row.Mdns,
                Runs=row.Runs,
                Wkts=row.Wkts,
                BBI=row.BBI,
                Ave=row.Ave,
                Econ=row.Econ,
                SR=row.SR,
                fours=row.fours,
                fives=row.fives
            )
        )

    Bowling.objects.bulk_create(objs, batch_size=1000)

class Command(BaseCommand):
    help = "Load Batting, Bowling, and Fielding data"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.stdout.write("Loading Fielding...")
            load_fielding()

            self.stdout.write("Loading Batting...")
            load_batting()

            self.stdout.write("Loading Bowling...")
            load_bowling()

        self.stdout.write(self.style.SUCCESS("All cricket data loaded successfully"))
