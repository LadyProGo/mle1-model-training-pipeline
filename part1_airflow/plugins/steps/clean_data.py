"""Data cleaning functions for the MLE1 real estate project."""

import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove fully duplicated rows and duplicates by flat_id."""
    df_clean = df.copy()

    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean.drop_duplicates(subset=["flat_id"])

    return df_clean


def remove_invalid_price(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with unrealistically low apartment prices."""
    df_clean = df.copy()

    df_clean = df_clean[df_clean["price"] >= 100000]

    return df_clean


def fix_ceiling_height(df: pd.DataFrame) -> pd.DataFrame:
    """Fix ceiling height values that appear to be recorded with a scale error."""
    df_clean = df.copy()

    mask = df_clean["ceiling_height"].between(20, 60)
    df_clean.loc[mask, "ceiling_height"] = df_clean.loc[mask, "ceiling_height"] / 10

    return df_clean


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all data cleaning steps sequentially."""
    df_clean = df.copy()

    df_clean = remove_duplicates(df_clean)
    df_clean = remove_invalid_price(df_clean)
    df_clean = fix_ceiling_height(df_clean)

    return df_clean
