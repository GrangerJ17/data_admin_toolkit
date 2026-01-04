from helper_functions import is_text_value, clean_text
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import dns.resolver
import pandas as pd
import numpy as np
import math
import re

def is_predominantly_lowercase(s, threshold=0.8):
    alphabetic_chars = [c for c in s if c.isalpha()] 
    
    if not alphabetic_chars:
        return False 
        
    lowercase_count = sum(1 for c in alphabetic_chars if c.islower())
    total_alphabetic_count = len(alphabetic_chars)
    
    return (lowercase_count / total_alphabetic_count) >= threshold

def check_email_format(items: list )-> int:
    count = 0
   
    for item in items:
        if "@" in item:
            count += 0.25
        if "." in item:
            count += 0.25
        if is_predominantly_lowercase(item):
            count += 0.25
        email_pattern = r'^([a-z0-9_.-]+)@([a-z0-9-._]+)\.([a-z]{1,3})$'
        if bool(re.match(email_pattern, item)):
            count += 0.25

    return count

def check_phone_format(items: list )-> int:
    count = 0
    for item in items:

        item.replace("/[_-\./s]", "")
        if "+" in item:
            count += 0.5
            item = item.replace("+", "")
        if item.isdigit():
            count += 0.5
    
    return count

def check_numeric(test_row):
    count = 0
    for item in test_row:
        item = item.strip(",").strip(".").strip(" ").strip("$")
        if item.isdigit():
            count += 1

    return count

        


def column_classification(df: pd.DataFrame) -> dict:
    column_mapping = {"date": [],
                      "email": [],
                      "phone": [],
                      "text": [],
                      "numeric": [],
                      "unknown": []
                      }
    
    for col in df:
        test_row = []
        for i, item in enumerate(df[col]):
            if i >= 50:
                break
            test_row.append(item)

        counts = [check_email_format(test_row), 
                check_phone_format(test_row), 
                check_numeric(test_row)]






def standardise_date(df: pd.DataFrame, preferred_date_format: str = None):
    if preferred_date_format is None:
        preferred_date_format = "%d/%m/%Y"

    date_regex = re.compile(r'date', re.IGNORECASE)

    date_columns_df = [col for col in df.columns if date_regex.search(col)]

    for col in date_columns_df: 

        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].dt.strftime(preferred_date_format)

    return df

def clean_email(df: pd.DataFrame):
    email_regex = re.compile(r'\b\w*[-_]?email\b', re.IGNORECASE)
    email_columns_df = [col for col in df.columns if email_regex.search(col)]



    valid_email_tlds = []

    with open("./cache_data/live_valid_tlds.txt", "r") as f:
        valid_email_tlds = [str("." + line.strip()) for line in f]



    for col in email_columns_df:
        active_col = df[col].to_list()
        valid_emails = []
        
        for email in active_col:
            email = str(email)
            email = email.lower().strip().lstrip()
            if isinstance(email, str) and '@' in email and any(email.endswith(domain) for domain in valid_email_tlds):
                email_pattern = r'^([a-z0-9_.-]+)@([a-z0-9-._]+)\.([a-z]{1,3})$'
                if bool(re.match(email_pattern, email)):
                    valid_emails.append(email)
                else:
                    valid_emails.append("NaN")
            else:
                valid_emails.append("NaN")

        loc = df.columns.get_loc(col)
        valid_name = str(col+"_valid")
        df.insert(loc=loc+1, column=valid_name, value=valid_emails)

    return df

def format_text(df: pd.DataFrame):
    for col in df.columns:
        df[col] = df[col].apply(clean_text)
    return df

def fix_phones(df: pd.DataFrame):

    phone_pattern = re.compile(
    r'(phone|tel|telephone|mobile|cell|contact|mob)\s*[\#\-_]?\s*(no|number)?', 
    re.IGNORECASE
)

    phone_cols = [str(num) for num in df.columns if phone_pattern.search(num)]

    for col in phone_cols:
        df[str(col+"_valid")] = (df[col]
                            .str.replace(r'[\s\-._]+', '', regex=True)
                            .str.extract('^(?P<prefix>\+61)?0?(?P<number>\d+)') # extract prefix/number
                            .fillna({'prefix': '+61 '}) # replace prefix
                            .apply(lambda x: ''.join(str(i) for i in x), axis=1)    # join to form number
                        )
        
    return df

def drop_dups(df: pd.DataFrame, dedup_based_on: list = ['name', 'email', 'phone_valid']):
    return df.drop_duplicates(subset=dedup_based_on)

df = pd.read_csv("./messy_sheets_simple/messy_contacts.csv")

column_classification(df)




#TODO: Remove phone code from NaN phone entries/ dyanmically apply phone location code based on number style
# Handle acryonym formatting












