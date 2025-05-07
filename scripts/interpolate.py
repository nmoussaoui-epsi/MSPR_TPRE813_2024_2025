import pandas as pd

def interpolate_missing_years(df: pd.DataFrame, year_col: str, value_col: str, target_years: list) -> pd.DataFrame:
    """
    Remplit les années manquantes par interpolation linéaire ou extrapolation si nécessaire.
    """
    df = df.copy()
    df = df[[year_col, value_col]]
    df = df[df[year_col].notna()]
    df[year_col] = df[year_col].astype(int)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    df = df.set_index(year_col).sort_index()
    df = df.reindex(range(min(target_years), max(target_years) + 1))
    df[value_col] = df[value_col].interpolate(method="linear", limit_direction="both")
    df = df.loc[target_years]
    df = df.reset_index().rename(columns={"index": year_col})

    return df
