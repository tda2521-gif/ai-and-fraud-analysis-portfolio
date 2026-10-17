"""
Inputs (raw .xlsx, original company data headers like "(best_edgar_ticker) TICKER"):
    audit-comp.xlsx, comp-fraud.xlsx, computext_us.xlsx
Outputs:
    dataset.csv      (open in Excel with CUSIP imported as Text)
    dataset.csv.gz   (same data, compressed; pandas reads it directly; fits GitHub's file limit)

Usage:  python build_dataset.py <audit.xlsx> <fraud.xlsx> <text.xlsx> [outdir]
"""

# LOAD: write the combined dataset
    # CSV copies use ISO date strings so every tool reads the dates the same way
    out = final.copy()
    out["FILE DATE"] = out["FILE DATE"].dt.strftime("%Y-%m-%d")
    out["EVENT DATE"] = pd.to_datetime(out["EVENT DATE"]).dt.strftime("%Y-%m-%d")
    out.to_csv(f"{outdir}/dataset.csv", index=False)
    out.to_csv(f"{outdir}/dataset.csv.gz", index=False, compression="gzip")


# Run summary (informational only)

def report(final):
    k = final[~final["_key_incomplete"]]
    print("total rows:", len(final), "| keyed:", len(k), "| key-incomplete:", int(final["_key_incomplete"].sum()))
    print("audit+fraud linked rows (all):", int((final._in_audit & final._in_fraud).sum()),
          "| of which lack CUSIP/TICKER (linked via FKEY only):",
          int((final._in_audit & final._in_fraud & final._key_incomplete).sum()))
    print("all three:", int((k._in_text & k._in_audit & k._in_fraud).sum()),
          "| text+audit:", int((k._in_text & k._in_audit).sum()),
          "| text+fraud:", int((k._in_text & k._in_fraud).sum()),
          "| audit+fraud:", int((k._in_audit & k._in_fraud).sum()))


def main(audit_p, fraud_p, text_p, outdir="."):
    audit, fraud, text = extract(audit_p, fraud_p, text_p)
    final = transform(audit, fraud, text)
    load(final, outdir)
    report(final)


if __name__ == "__main__":
    a, f, t = sys.argv[1:4]
    main(a, f, t, sys.argv[4] if len(sys.argv) > 4 else ".")