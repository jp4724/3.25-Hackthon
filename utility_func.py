import pandas as pd


def split_code(value):
    """Accept a 3- or 6-digit number; split 6 digits into a tuple."""
    s = str(value).strip()
    if not s.isdigit():
        raise ValueError("Input must contain only digits")
    if len(s) == 3:
        return int(s)
    if len(s) == 6:
        return int(s[:3]), int(s[3:])
    raise ValueError("Input length must be 3 or 6 digits")

def normalize_time_period(x):
    s = str(x).strip()
    if s in {"2017", "2018"}:
        return "2017-2018"
    if s == "2021":
        return "2021-2022"
    return s

def expand_rows_by_geotype(df: pd.DataFrame, geotype_col: str = "GeoID") -> pd.DataFrame:
    """Expand rows when GeoType/GeoID contains 6 or 9 digits."""
    if geotype_col not in df.columns:
        raise KeyError(f"Column '{geotype_col}' was not found in DataFrame")

    rows = []
    for _, row in df.iterrows():
        value = row[geotype_col]
        value_str = str(value).strip()

        if value_str.isdigit() and len(value_str) == 6:
            left_code, right_code = split_code(value_str)
            for code in (left_code, right_code):
                new_row = row.copy()
                new_row[geotype_col] = code
                rows.append(new_row)
        elif value_str.isdigit() and len(value_str) == 9:
            codes = [int(value_str[i : i + 3]) for i in range(0, 9, 3)]
            for code in codes:
                new_row = row.copy()
                new_row[geotype_col] = code
                rows.append(new_row)
        else:
            rows.append(row.copy())

    return pd.DataFrame(rows).reset_index(drop=True)

def clean_percent_column(df: pd.DataFrame, column_name: str = "Percent") -> pd.DataFrame:
    """If the 'Percent' column exists, clean it. Otherwise, do nothing and return the DataFrame."""
    if column_name in df.columns:
        df[column_name] = (
            df[column_name]
            .str.replace(r"\(.*\)", "", regex=True)
            .str.replace(r"[^0-9.]", "", regex=True)
            .astype(float)
        )
    return df
