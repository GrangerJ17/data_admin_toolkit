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




'''
LAYER 5: DATA WRITER
────────────────────
write_to_csv(data_list, filename)
├─ Input: List of dicts [{field: value}, ...]
├─ Role: Convert to CSV
└─ Output: CSV file


MAIN WORKFLOW
─────────────
for each url in url_list:
    html = fetch_page(url, wait_for="target_selector")
    dom = parse_html(html)
    data = extract_fields(dom, selector_map)
    cleaned_data = {k: clean_text(v) for k, v in data.items()}
    append to results_list
    
write_to_csv(results_list, "output.csv")


MINIMAL CONFIG EXAMPLE
──────────────────────
selector_map = {
    "title": "h1.product-title",
    "price": "span.price",
    "description": "div.product-desc p"
}

urls = ["https://example.com/item1", "https://example.com/item2"]

scrape(urls, selector_map, output="data.csv")'''

