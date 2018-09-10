import pandas as pd
from incf.countryutils import transformations
import copy
import pickle
import os

import country_helper_functions as chf

from IPython.display import display, Markdown

def printmd(string):
    display(Markdown(string))

base_tmp_dir = os.path.join(os.getenv('TEST_TMPDIR', '/tmp'),'chloropleth')
if not os.path.exists(base_tmp_dir):
    os.makedirs(base_tmp_dir)

class IEA_data():

    def __init__(self):
        self.country_iso3_list = chf.countries_keyed_by_code.keys()

        self.load_IEA_data()
        self.parse_IEA_countries()

        self.Products = self.df1.Product.unique()
        self.Flows = self.df1.Flow.unique()
        
    def load_IEA_data(self):
        processed_filename = os.path.join(base_tmp_dir,'IEA_EnergyData_2017.pkl')
        try:
            self.df1 = pd.read_pickle(processed_filename) 
        except:
            datafile = 'raw_data/IEA_HeadlineEnergyData_2017.xlsx'
            xl = pd.ExcelFile(datafile)
            self.df1 = xl.parse('TimeSeries_1971-2016',skiprows=1)
            self.df1.to_pickle(processed_filename)

        self.years = range(1971,2017)
    
    def print_summary(self):
        print("Loaded the IEA 2017 dataset, which is divided into the following Products and Flows")
        printmd("**Products**")
        for name in self.Products : print name 
        printmd("**Flows**")
        for name in self.Flows: print name 

    def parse_IEA_countries(self):
        processed_filename = os.path.join(base_tmp_dir,'IEA_countries_2017.pkl')
        try:
            with open(processed_filename, "rb") as f:
                (self.iea_specified_country_codes, self.iea_country_codes_to_named_region, self.african_country_codes, self.non_oecd_americas_country_codes) = pickle.load(f) 
        except:
                
            # Sort the IEA data in some not insane way
            middle_eastern_countries = ['Bahrain', 'Iran', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 'Oman', 'Qatar', 'Saudi Arabia', 'Syrian Arab Republic', 'United Arab Emirates', 'Yemen']
            non_OECD_Eurasian_countries = ['Albania', 'Armenia', 'Azerbaijan', 'Belarus', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Macedonia', 'Georgia', 'Gibraltar', 'Kazakhstan', 'Kyrgyzstan', 'Lithuania', 'Malta', 'Moldova', 'Montenegro', 'Romania', 'Russian Federation', 'Serbia', 'Tajikistan', 'Turkmenistan', 'Ukraine', 'Uzbekistan']
            non_OECD_asia = ['Bangladesh', 'Brunei Darussalam', 'Cambodia', 'Democratic People\xe2\x80\x99s Republic of Korea', 'India', 'Indonesia', 'Malaysia', 'Mongolia', 'Myanmar', 'Nepal', 'Pakistan', 'Philippines', 'Singapore', 'Sri Lanka', 'Taiwan, province of china', 'Thailand', 'Vietnam', 'Afghanistan', 'Bhutan', 'Cambodia', 'Cook Islands', 'Fiji', 'French Polynesia', 'Kiribati', "Lao People's Democratic Republic", 'Macao', 'Maldives', 'Mongolia', 'New Caledonia', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Vanuatu']

            middle_eastern_country_codes = [chf.find_country_by_name(country) for country in middle_eastern_countries]
            non_OECD_Eurasian_country_codes = [chf.find_country_by_name(country) for country in non_OECD_Eurasian_countries]
            non_OECD_asia_country_codes = [chf.find_country_by_name(country) for country in non_OECD_asia]

            self.iea_specified_country_codes = {}
            for country in self.df1.Country.unique().tolist():
                try:
                    code = chf.find_country_by_name(country)
                    self.iea_specified_country_codes[code] = country
                except:
                    pass
            self.iea_specified_country_codes[u'CHN'] = "People's Republic of China"
            self.iea_specified_country_codes[u'KOR'] = "Korea"
            self.iea_specified_country_codes[u'SVK'] = "Slovak Republic"
            self.iea_specified_country_codes[u'CZE'] = "Czech Republic"

            self.iea_country_codes_to_named_region = copy.deepcopy(self.iea_specified_country_codes)
            self.iea_country_codes_to_named_region[u'HKG'] = "People's Republic of China"

            self.iea_country_codes_to_named_region.update({code:'Middle East' for code in middle_eastern_country_codes})
            self.iea_country_codes_to_named_region.update({code:'Non-OECD Europe and Eurasia' for code in non_OECD_Eurasian_country_codes})
            self.iea_country_codes_to_named_region.update({code:'Non-OECD Asia' for code in non_OECD_asia_country_codes})

            self.african_country_codes = []
            self.non_oecd_americas_country_codes = []
            for iso3 in self.country_iso3_list:
                if iso3 not in self.iea_country_codes_to_named_region:
                    try:
                        cont_code = transformations.cca_to_ctca2(iso3)
                        if cont_code == u'AF':
                            self.iea_country_codes_to_named_region[iso3]='Africa'
                            self.african_country_codes.append(iso3)
                        elif cont_code == u'NA' or cont_code == u'SA':
                            self.iea_country_codes_to_named_region[iso3]='Non-OECD Americas'
                            self.non_oecd_americas_country_codes.append(iso3)
                    except:
                        pass
            with open(processed_filename, 'wb') as f:
                pickle.dump((self.iea_specified_country_codes, self.iea_country_codes_to_named_region, self.african_country_codes, self.non_oecd_americas_country_codes),f)



    def get_IEA_data_for_countries(self,database, country_code, year): 
        try:
            region = self.iea_country_codes_to_named_region[country_code]
        except:
            raise ValueError("Couldn't find country data for %s" % self.iea_country_codes_to_named_region[country_code])

        return database.loc[region,year]




