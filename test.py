import pandas as pd 

df = pd.read_feather(r"dataset\2025\JAN\01\banknifty_put.feather")

# --- Fix multi-index columns if any ---
if isinstance(df.columns, pd.MultiIndex):
    new_col = []
    for col in df.columns:
        if col[0] != "":
            new_col.append(col[0])
        else:
            new_col.append(col[1])
    df.columns = new_col

# --- Reorder columns ---
re_ordered_data = ['date', 'time', 'symbol', 'strike', 'expiry',
                   'open', 'high', 'low', 'close', 'volume', 'oi']
existing_cols = [col for col in re_ordered_data if col in df.columns]
df = df[existing_cols]

# --- Print outputs ---
print(df.columns.to_list())
df=df.head(10)
# ✅ Print first row as tuple
first_row = tuple(
    float(x) if isinstance(x, (int, float)) else int(x) if str(x).isdigit() else str(x)
    for x in df.values.tolist()
)
print(first_row)
