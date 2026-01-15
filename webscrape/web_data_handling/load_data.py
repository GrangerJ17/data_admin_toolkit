import pandas as pd
import numpy as np

def clean_data(extracted_data):

    for k, v in extracted_data.items():
        new_values = []
        for value in v:
            new_values.append(value.strip().lstrip().replace("\n", " "))

        extracted_data[k] = new_values

    return extracted_data


def write_to_csv(data_list, filename):

    for k, v in data_list.items():
        print(k, "==\n\n", v, "\n\n")

    df = pd.DataFrame({k: pd.Series(v) for k, v in data_list.items()})


    csv = df.to_csv(filename)

    return csv




