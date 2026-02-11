import io
import json
import os
from datetime import datetime, timezone

import pandas as pd
from azure.storage.blob import BlobServiceClient

DEFAULT_AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)


def process_nutritional_data_from_azurite(
    container_name: str = "datasets",
    blob_name: str = "All_Diets.csv",
    output_dir: str = "simulated_nosql",
) -> dict:
    """Reads All_Diets.csv from Azurite Blob Storage, computes insights, and saves results as JSON.
    Returns the results as a Python dict (useful for printing/logging).
    """

    connect_str = os.getenv("AZURITE_CONNECTION_STRING", DEFAULT_AZURITE_CONNECTION_STRING)

    # Connect to Azurite
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)

    # Download blob -> bytes
    blob_client = container_client.get_blob_client(blob_name)
    stream = blob_client.download_blob().readall()

    # Load dataset into pandas
    df = pd.read_csv(io.BytesIO(stream))

    # Clean: convert macro columns to numeric and fill missing with means
    macro_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
    for col in macro_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df[macro_cols] = df[macro_cols].fillna(df[macro_cols].mean(numeric_only=True))

    # Add ratios (avoid division by zero)
    df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"].replace(0, pd.NA)
    df["Carbs_to_Fat_ratio"] = df["Carbs(g)"] / df["Fat(g)"].replace(0, pd.NA)

    # Insights
    avg_macros = df.groupby("Diet_type")[macro_cols].mean().reset_index()

    top5_protein = (
        df.sort_values("Protein(g)", ascending=False)
        .groupby("Diet_type", as_index=False)
        .head(5)[["Diet_type", "Recipe_name", "Cuisine_type", "Protein(g)", "Carbs(g)", "Fat(g)"]]
    )

    highest_avg_protein_diet = (
        avg_macros.sort_values("Protein(g)", ascending=False).iloc[0]["Diet_type"]
        if len(avg_macros) else None
    )

    most_common_cuisines = (
        df.groupby("Diet_type")["Cuisine_type"]
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={"Cuisine_type": "Most_common_cuisine"})
    )

    # Prepare output
    run_meta = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"container": container_name, "blob": blob_name},
        "rows_processed": int(len(df)),
    }

    results = {
        "meta": run_meta,
        "avg_macros_by_diet_type": avg_macros.to_dict(orient="records"),
        "top5_protein_recipes_by_diet_type": top5_protein.to_dict(orient="records"),
        "diet_type_with_highest_avg_protein": highest_avg_protein_diet,
        "most_common_cuisine_by_diet_type": most_common_cuisines.to_dict(orient="records"),
    }

    # Save to simulated NoSQL (JSON files)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Also save a smaller file just for averages (handy for screenshots)
    with open(os.path.join(output_dir, "avg_macros.json"), "w", encoding="utf-8") as f:
        json.dump(avg_macros.to_dict(orient="records"), f, indent=2)

    return results


if __name__ == "__main__":
    output = process_nutritional_data_from_azurite()
    print("✅ Processed data from Azurite and saved JSON to ./simulated_nosql/")
    print(f"Rows processed: {output['meta']['rows_processed']}")
    print(f"Diet type with highest avg protein: {output['diet_type_with_highest_avg_protein']}")
