from pathlib import Path
import pandas as pd

raw = Path("data/raw")
out = Path("data/processed")
out.mkdir(parents=True, exist_ok=True)

for f in raw.glob("*.xls*"):
    sheets = pd.read_excel(f, sheet_name=None)  # every sheet
    for name, df in sheets.items():
        # tidy column names: lowercase, underscores
        df.columns = (df.columns.astype(str).str.strip().str.lower()
                      .str.replace(r"[^0-9a-z]+", "_", regex=True).str.strip("_"))
        df = df.dropna(how="all")                 # drop empty rows
        suffix = "" if len(sheets) == 1 else f"_{name.lower().replace(' ', '_')}"
        df.to_csv(out / f"{f.stem}{suffix}.csv", index=False)
        print(f"{f.name} [{name}] -> {len(df)} rows")

Run it from the repo root: