import pandas as pd

def extract_data():
    # read input data from csv file
    data = pd.read_csv("input.csv")
    print("Data extracted")
    return data