"""
Derived columns added in transform():
    PERCENTAGE OF AUDIT FEES = LATEST AUDIT FEES SUM / LATEST TOTAL FEES SUM   (blank where total = 0)
    MENTIONS AI (1/0)        = 1 if SENTENCE mentions AI / A.I. / Artificial Intelligence / GenAI

Inputs (raw .xlsx, original company data headers like "(best_edgar_ticker) TICKER"):
    audit-comp.xlsx, comp-fraud.xlsx, computext_us.xlsx
Outputs:
    dataset.csv      (open in Excel with CUSIP imported as Text)
    dataset.csv.gz   (same data, compressed; pandas reads it directly; fits GitHub's file limit)

Usage:  python build_dataset.py <audit.xlsx> <fraud.xlsx> <text.xlsx> [outdir]
"""

# TRANSFORM: deduplicate, link audit<->fraud, join text, flag, order and type the result
# Searched keywords for the "MENTIONS AI" column.
# label -> regex. A sentence is flagged 1 if ANY pattern matches.
KEYWORDS = {
    # "AI" as a standalone word, any capitalization (AI, ai, AIs; AI-powered and AI's also match).
    # Words that merely contain the letters (said, retail, Air) do not match.
    '"AI" (standalone word)': r'(?<![A-Za-z0-9])(?i:ais?)(?![A-Za-z0-9])',
    '"A.I."':                  r'(?<![A-Za-z0-9])A\.I\.?(?![A-Za-z0-9])',
    '"Artificial Intelligence" (any capitalization)':
                               r'(?i:\bartificial[\s\-]+intelligence\b)',
    '"GenAI" / "Gen-AI"':      r'(?i:\bgen-?ai\b)',
}
AI_REGEX = re.compile("|".join(KEYWORDS.values()))


def add_audit_pct(df):
    """Audit fees as a share of total fees (blank where total fees = 0)."""
    out = df.copy()
    total = out["LATEST TOTAL FEES SUM"].replace(0, np.nan)  # avoid divide-by-zero
    out[PCT_COL] = out["LATEST AUDIT FEES SUM"] / total
    return out


def add_ai_flag(df):
    """Binary flag: does SENTENCE mention AI / A.I. / Artificial Intelligence / GenAI?"""
    out = df.copy()
    out[AI_COL] = out["SENTENCE"].fillna("").astype(str).str.contains(AI_REGEX).astype(int)
    return out


def split_by_key(d):
    """Rows with all three keys can be joined to text; the rest are set aside (not dropped)."""
    ok = d[KEYS].notna().all(axis=1)
    return d[ok].copy(), d[~ok].copy()


def transform(audit, fraud, text):
    # --- deduplicate exact repeats ---------------------------------------------------
    n_in = {"audit": len(audit), "fraud": len(fraud), "text": len(text)}
    audit, fraud, text = (d.drop_duplicates().reset_index(drop=True) for d in (audit, fraud, text))
    print("rows in:", n_in, "-> after exact-duplicate removal:",
          {"audit": len(audit), "fraud": len(fraud), "text": len(text)})

    # --- derived columns (computed per source table, before the merges carry them along) ---
    audit = add_audit_pct(audit)
    text = add_ai_flag(text)

    # --- 1) audit x fraud: link on COMPANY FKEY + FILE DATE --------------------------
    af = audit.merge(fraud, on=FKEY_DATE, how="outer", suffixes=("_a", "_f"), indicator="_af")
    af["_in_audit"] = af["_af"].isin(["both", "left_only"])
    af["_in_fraud"] = af["_af"].isin(["both", "right_only"])
    for c in ("CUSIP", "TICKER"):
        af[c] = af[f"{c}_a"].combine_first(af[f"{c}_f"])
        af = af.drop(columns=[f"{c}_a", f"{c}_f"])
    af = af.drop(columns="_af")

    # --- 2) text x (audit+fraud): join on CUSIP + FILE DATE + TICKER -----------------
    (af_ok, af_bad), (t_ok, t_bad) = split_by_key(af), split_by_key(text)

    m = t_ok.merge(af_ok, on=KEYS, how="outer", indicator="_t")
    m["_in_text"] = m["_t"].isin(["both", "left_only"])
    for c in ("_in_audit", "_in_fraud"):
        m[c] = m[c].fillna(False).astype(bool)
    m = m.drop(columns="_t")
    m["_key_incomplete"] = False

    # rows lacking CUSIP or TICKER cannot be matched to text: keep them, flagged, instead of dropping
    af_bad = af_bad.assign(_key_incomplete=True, _in_text=False)
    t_bad = t_bad.assign(_key_incomplete=True, _in_text=True, _in_audit=False, _in_fraud=False)

    final = pd.concat([m, af_bad, t_bad], ignore_index=True)
    for c in FLAGS:
        final[c] = final[c].fillna(False).astype(bool)

    # --- 3) column order, types and row order ----------------------------------------
    lead = ["TICKER", "CUSIP", "FILE DATE", "COMPANY FKEY", "GVKEY"]
    fraud_cols = [c for c in final.columns if c.startswith("NOTEFFECTIVEFINANCIALFRAUD")]
    for c in AUDIT_COLS + ["NOTEFFECTIVEFINANCIALFRAUD", AI_COL]:
        final[c] = final[c].astype("Int64")        # whole numbers, blanks stay blank (no '969777.0')
    final = final[lead + TEXT_COLS + [AI_COL] + AUDIT_COLS + [PCT_COL] + fraud_cols + FLAGS]
    return final.sort_values(["CUSIP", "FILE DATE"], na_position="last", kind="stable").reset_index(drop=True)