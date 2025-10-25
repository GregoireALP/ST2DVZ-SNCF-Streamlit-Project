import pandas as pd
from io import StringIO
import re

def load_data():
    """Load and clean data from a CSV file."""
    
    pattern = re.compile(r"^20\d{2}-\d{2}")
    path = "C:/Users/grego/Documents/GitHub/ST2DVZ-SNCF-Streamlit-Project/data/data.csv"
    clean_lines = []
    expected_cols = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header = lines[0]
    clean_lines.append(header)

    for line in lines[1:]:
        if pattern.match(line.strip()):
            n_cols = line.count(";") + 1
            if expected_cols is None:
                expected_cols = header.count(";") + 1
            if n_cols == expected_cols:
                clean_lines.append(line)

    return pd.read_csv(StringIO("".join(clean_lines)), sep=";")



def process_data(df):
    df = df.drop(columns=['Commentaire annulations', 'Commentaire retards au départ'])
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
    

    # Drop all rows with negative values in numeric columns
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    df = df[(df[num_cols] >= 0).all(axis=1)]
    df.reset_index(drop=True, inplace=True)
    
    return df


def get_locations():
    path = "C:/Users/grego/Documents/GitHub/ST2DVZ-SNCF-Streamlit-Project/data/locations.csv"
    df = pd.read_csv(path, sep=",")
    return df
