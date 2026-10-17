"""
Merge the three raw company data exports into one dataset.

    audit <-> fraud : COMPANY FKEY + FILE DATE   (links row across sheets when CUSIP/TICKER is blank)
    text  <-> others: CUSIP + FILE DATE + TICKER

Inputs (raw .xlsx, original company data headers like "(best_edgar_ticker) TICKER"):
    audit-comp.xlsx, comp-fraud.xlsx, computext_us.xlsx
Outputs:
    dataset.csv      (open in Excel with CUSIP imported as Text)
    dataset.csv.gz   (same data, compressed; pandas reads it directly; fits GitHub's file limit)
    
Usage:  python build_dataset.py <audit.xlsx> <fraud.xlsx> <text.xlsx> [outdir]
"""

import re
import sys

import numpy as np
import pandas as pd

KEYS = ["CUSIP", "FILE DATE", "TICKER"]          # text <-> (audit/fraud) join keys
FKEY_DATE = ["COMPANY FKEY", "FILE DATE"]        # audit <-> fraud join keys

TEXT_COLS = ["EVENT DATE", "DATA ITEM NAME", "TERM_POLARITY", "REASON_POLARITY", "SENTENCE"]
AUDIT_COLS = ["LATEST AUDIT FEES SUM", "LATEST TOTAL FEES SUM", "AUDIT FEES", "TOTAL FEES"]
PCT_COL = "PERCENTAGE OF AUDIT FEES"
AI_COL = "MENTIONS AI (1=yes, 0=no)"
FLAGS = ["_in_text", "_in_audit", "_in_fraud", "_key_incomplete"]


#read the raw xlsx files and standardize types, names and identifiers

def strip_prefix(col):
    """'(best_edgar_ticker) TICKER' -> 'TICKER'"""
    return re.sub(r"^\([^)]*\)\s*", "", str(col)).strip()


def read_raw(path, str_cols, rename=None, positional_names=None):
    # ID columns (by position) are read as text so pandas cannot turn '0001219120'
    # into 1219120 or '000361105' into 361105
    d = pd.read_excel(path, dtype={i: str for i in str_cols}, engine="openpyxl")
    if positional_names:
        # computext_us.xlsx headers are long descriptions, so name them by position
        assert len(positional_names) == d.shape[1], "unexpected column count"
        d.columns = positional_names
    else:
        d.columns = [strip_prefix(c) for c in d.columns]
    if rename:
        d = d.rename(columns=rename)
    for c in ("TICKER", "CUSIP"):
        d[c] = d[c].astype("string").str.strip().str.upper().replace("", pd.NA)
    d["FILE DATE"] = pd.to_datetime(d["FILE DATE"]).dt.normalize()
    return d


def extract(audit_p, fraud_p, text_p):
    audit = read_raw(audit_p, [0, 4, 7], rename={"CUSIP NUMBER": "CUSIP"})   # ticker, cusip, company_fkey
    fraud = read_raw(fraud_p, [0, 2, 6], rename={"CUSIP NUMBER": "CUSIP"})   # ticker, cusip, company_fkey
    text = read_raw(
        text_p, [0, 2],                                                      # ticker, cusip
        positional_names=["TICKER", "FILE DATE", "CUSIP", "GVKEY", "EVENT DATE",
                          "DATA ITEM NAME", "TERM_POLARITY", "REASON_POLARITY", "SENTENCE"],
    )
    text["GVKEY"] = text["GVKEY"].astype("Int64")   # numeric in the source; Int64 avoids '144001.0'
    return audit, fraud, text

