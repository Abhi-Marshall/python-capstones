import pandas as pd

def load_data(df):
    # save transformed data into new file
    df.to_csv("output.csv", index=False)
    print("Data loaded to output.csv")