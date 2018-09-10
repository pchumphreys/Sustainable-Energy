import pycountry
import csv
import jellyfish

countries_keyed_by_name = {(country.name.lower()):country.alpha_3 for country in list(pycountry.countries)}
countries_keyed_by_code = {country.alpha_3:(country.name.lower()) for country in list(pycountry.countries)}
country_iso3_list = countries_keyed_by_code.keys()

def correct_country_mispelling(s):
    with open("misc/ISO3166ErrorDictionary.csv", "rb") as info:
        reader = csv.reader(info)
        for row in reader:
            if fuzzy_match(s.lower().decode('utf-8'),remove_non_ascii(row[0]).lower().decode('utf-8'),0.95):
                return row[2].lower()
    return s

# hat tip to http://stackoverflow.com/a/1342373/2367526
def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)
 
def fuzzy_match(s1, s2, max_dist=.9):
    return jellyfish.jaro_distance(s1, s2) >= max_dist

def find_country_by_name(s): 

        s = remove_non_ascii(s).lower()
        s = correct_country_mispelling(s)

        matching = [x for x in countries_keyed_by_name if fuzzy_match(s.decode('utf-8'), x,0.95)]
        
        if len(matching) == 1:
            return countries_keyed_by_name[matching[0]]
        elif len(matching) > 1:
            raise LookupError('More than one country found!: ', matching)
        else:
            raise LookupError('No country found for: ', s)
        
def match_country_by_code_or_name(code,name = ''):
    try:
        country = pycountry.countries.lookup(code).alpha_3
    except:
        
        try:
            country = find_country_by_name(name)
        except:
            raise LookupError('Failed to match country')
    return country   