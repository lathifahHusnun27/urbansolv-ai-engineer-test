from fastapi import FastAPI
import pandas as pd
from pathlib import Path
from typing import Optional

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "clean_data.csv"

#print(DATA_PATH)

df = pd.read_csv(DATA_PATH)

#print(df["jenis_bisnis"].value_counts(dropna=False))

#print("\nNama bisnis yang mengandung bakmi/bakmie:")
#print(
#    df[df["nama_tempat"].str.contains(
#        "bakmi|bakmie", case=False, na=False
#    )]["nama_tempat"]
#)

#print("\nNama bisnis yang mengandung ramen:")

#print(
#    df[df["nama_tempat"].str.contains(
#        "ramen", case=False, na=False
#    )]["nama_tempat"]
#)

#print("NaN:", df.isna().sum().sum())
#print("Inf:", df.isin([float("inf"), float("-inf")]).sum().sum())

#print(df.shape)
#print(df.columns.tolist())


@app.get("/")
def read_root():
    return {"message": "UrbanSolv API is running"}


@app.get("/businesses")
def get_businesses():
    data = df.to_dict(orient="records")
    data = [{k: None if pd.isna(v) else v for k, v in row.items()} for row in data]
    return data

@app.get("/businesses/search")
def search_businesses(
    keyword: Optional[str] = None,
    kelurahan: Optional[str] = None,
    kecamatan: Optional[str] = None,
    rating: Optional[float] = None,
    jumlah_review: Optional[float] = None,
    harga: Optional[str] = None
):
    result = df.copy()

    if keyword:
        result = result[
            result["nama_tempat"].str.contains(keyword, case=False, na=False)]

    if kelurahan:
        result = result[result["kelurahan"].str.contains(kelurahan, case=False, na=False)]

    if kecamatan:
        result = result[result["kecamatan"].str.contains(kecamatan, case=False, na=False)]

    if rating is not None:
        result = result[result["rating"] >= rating]

    if jumlah_review is not None:
        result = result[result["jumlah_review"] >= jumlah_review]

    if harga :
        result = result[
        result["harga"].astype(str).str.contains(str(harga), case=False, na=False)
    ]

    data = result.to_dict(orient="records")
    data = [
        {k: None if pd.isna(v) else v for k, v in row.items()}
        for row in data
    ]

    return data

@app.get("/statistics")
def get_statistics():
    return {
        "total_businesses": int(len(df)),
        "average_rating": float(df["rating"].mean()),
        "total_reviews": int(df["jumlah_review"].sum()),
        "total_bakmie": int(df["nama_tempat"].str.contains(
            "bakmie|bakmi", case=False, na=False, regex=True
        ).sum()),
        "total_ramen": int(df["nama_tempat"].str.contains(
            "ramen", case=False, na=False
        ).sum())
    }