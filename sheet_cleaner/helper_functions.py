from urllib.request import urlopen
import re

def download_valid_tlds():
    url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    with urlopen(url) as f:
        tlds = [line.decode("utf-8").lower() for line in f.readlines()[1:]]
        print(tlds)

    with open("./cache_data/live_valid_tlds.txt", "w") as f:
        for tld in tlds:
            f.write(str(tld))

def is_text_value(value):
    if not isinstance(value, str):
        return False

    if '@' in value:
        return False
    if value.replace(',', '').replace('.', '').isdigit():
        return False
    return True

def clean_text(value):
    if not is_text_value(value):
        return value
    value = value.strip()                   # remove leading/trailing whitespace
    value = re.sub('\s+', ' ', value)      # collapse multiple spaces
    value = value.title()                   # capitalize each word
    value = value.replace('.', '')          # remove dots if needed
    return value

download_valid_tlds()