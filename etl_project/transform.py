def transform_data(df):
    # increase salary by 10 percent
    df["salary"] = df["salary"] * 1.10
    print("Data transformed")
    return df