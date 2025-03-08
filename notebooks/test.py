#!/usr/bin/python3

import pandas as pd

df = pd.read_csv("../data/emails.csv").head()
print(df)
