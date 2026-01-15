from django.core.management.base import BaseCommand

import re

def parse_md(md_str):
    if not md_str:
        return None, None, None

    # Example: "5 (5ct 0st)"
    total_match = re.match(r"(\d+)", md_str)
    ct_match = re.search(r"(\d+)ct", md_str)
    st_match = re.search(r"(\d+)st", md_str)

    md_total = int(total_match.group(1)) if total_match else None
    md_ct = int(ct_match.group(1)) if ct_match else None
    md_st = int(st_match.group(1)) if st_match else None

    return md_total, md_ct, md_st


class Command(BaseCommand):
    help = "Cleans the Batting table or imports CSV"

    def handle(self, *args, **kwargs):
        import pandas as pd
        from core.models import Batting, Bowling, Fielding
        from django.db import transaction
        import numpy as np
        
        # Read CSV and normalize missing values
        from django.conf import settings
        import os
        
        csv_path = os.path.join(
            settings.BASE_DIR,
            "data",
            "Fielding_cleaned_v2.csv"
        )
        
        df = pd.read_csv(
            csv_path,
            index_col=0,
            na_values=["-", "NaN", "null", ""]
        )

        
        # Optional: rename CSV columns to match model
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
        
        # Convert NaN → None for Django
        df = df.replace({np.nan: None, '-': None})

        
        from psycopg2.extras import NumericRange

        def parse_span(span_str):
            if not span_str:
                return None
            start, end = span_str.split('-')
            return NumericRange(int(start), int(end), bounds='[]')

        
        
        
        
        
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
        
        
        with transaction.atomic():
            Fielding.objects.bulk_create(objs, batch_size=1000)
        self.stdout.write("Command ran successfully")
