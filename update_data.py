#THIS IS NOT ALL MY OWN WORK! https://gist.github.com/pdashford/2e4bcd4fc2343e2fd03efe4da17f577d and the associated videos helped me enormously with os stuff
import os
import pandas as pd
from datetime import datetime
import regex as re
import openpyxl

DATA_DIR = "data"
OUTPUT_FILE = f"{DATA_DIR}/monthly_data.csv"

def load_latest():
  files = [f for f in os.listdir(DATA_DIR) if f.endswith((".csv", ".xlsx"))]
  if not files:
    raise FileNotFound("No data files found in the data folder.")
  latest = max(files, key = lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
  path = os.path.join(DATA_DIR, latest)
  return pd.read_excel(path) if latest.endswith("xlsx") else pd.read_csv(path)

def process_data(df):
  df = df.replace(regex=r'(M|m)issing', value="")
  df = df.replace(regex=r'N/A', value = "")
  df = df.dropna()
  df["updated_at"] = datetime.utcnow()
  return df
  
def main():
  df = load_latest()
  df = process_data(df)
  df.to_csv(OUTPUT_FILE, index = False)
  print(f"Updated data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
  main()


