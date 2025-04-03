import pandas as pd


# Define chunk size (e.g., 10,000 rows at a time)
chunk_size = 150000
file_path = "../data/emails.csv"

# Read in chunks and process each part separately
for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    # print(chunk.info())
    email_df = chunk
    print("Email Dataset is ready to be processed")
    break  # Remove this once you're ready to process all chunks
