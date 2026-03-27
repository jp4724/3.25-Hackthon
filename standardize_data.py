from pathlib import Path
import geopandas as gpd
import pandas as pd
import utility_func


def extract_depression_from_geojson():
    # Extract depression data from geojson
    base_dir = Path("data/geojson")
    output_csv = Path("data/csv/clean/uhf42_depression_combined.csv")

    sources = [
        {
            "path": base_dir / "CHS_UHF42_Depression_Age_adjusted_Percent_2017_2018.geojson",
            "value_col": "Age_adjusted_Percent_2017_2018_Value",
            "year": "2017-2018",
        },
        {
            "path": base_dir / "CHS_UHF42_Depression_Age_adjusted_Percent_2021_2022.geojson",
            "value_col": "Age_adjusted_Percent_2021_2022_Value",
            "year": "2021-2022",
        },
    ]

    frames = []
    for src in sources:
        gdf = gpd.read_file(src["path"])

        df = gdf[["UHFCODE", "BOROUGH", src["value_col"]]].copy()
        df = df.rename(
            columns={
                "UHFCODE": "UHFCode",
                "BOROUGH": "Borough",
                src["value_col"]: "DepressionPercentValue",
            }
        )

        df["Year"] = src["year"]
        df = df[["UHFCode", "Year", "DepressionPercentValue", "Borough"]]

        # drop non-data rows like UHFCODE = 0 or missing values
        df = df.dropna(subset=["UHFCode", "DepressionPercentValue"])
        df = df[df["UHFCode"] > 0]

        frames.append(df)

    combined_df = pd.concat(frames, ignore_index=True)
    combined_df["UHFCode"] = combined_df["UHFCode"].astype(int)
    combined_df = combined_df.sort_values(["Year", "UHFCode"]).reset_index(drop=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_csv, index=False)

    print(f"Saved: {output_csv}")
    combined_df.head()

# Standardize raw CSV data
def standardize_raw_csv(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["TimePeriod"] = df["TimePeriod"].map(utility_func.normalize_time_period)
    df = utility_func.expand_rows_by_geotype(df)
    df = utility_func.clean_percent_column(df)
    return df