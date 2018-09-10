import wbpy
import pycountry
api = wbpy.IndicatorAPI()
import country_helper_functions as chf

countries_in_wb = [u'AGO', u'DZA', u'EGY', u'BGD', u'NER', u'LIE', u'NAM', u'BGR', u'BOL', u'GHA', u'PAK', u'CPV', u'JOR', u'LBR', u'LBY', u'MYS', u'DOM', u'PRI', u'PRK', u'PSE', u'TZA', u'BWA', u'KHM', u'NIC', u'TTO', u'ETH', u'PRY', u'HKG', u'SAU', u'LBN', u'SVN', u'BFA', u'CHE', u'MRT', u'HRV', u'CHL', u'CHN', u'KNA', u'SLE', u'JAM', u'SMR', u'GIB', u'DJI', u'GIN', u'FIN', u'URY', u'THA', u'STP', u'SYC', u'NPL', u'LAO', u'YEM', u'ZAF', u'KIR', u'PHL', u'SXM', u'ROU', u'VIR', u'SYR', u'MAC', u'MAF', u'MLT', u'KAZ', u'TCA', u'PYF', u'DMA', u'BEN', u'BEL', u'TGO', u'DEU', u'GUM', u'LKA', u'SSD', u'GBR', u'GUY', u'CRI', u'CMR', u'MAR', u'MNP', u'LSO', u'HUN', u'TKM', u'SUR', u'NLD', u'BMU', u'TCD', u'GEO', u'MNE', u'MNG', u'MHL', u'BLZ', u'MMR', u'AFG', u'BDI', u'VGB', u'BLR', u'GRD', u'GRC', u'RUS', u'GRL', u'AND', u'MOZ', u'TJK', u'HTI', u'MEX', u'ZWE', u'LCA', u'IND', u'LVA', u'BTN', u'VCT', u'VNM', u'NOR', u'CZE', u'ATG', u'FJI', u'HND', u'MUS', u'LUX', u'ISR', u'FSM', u'PER', u'IDN', u'VUT', u'MKD', u'COD', u'COG', u'ISL', u'COM', u'COL', u'NGA', u'TLS', u'PRT', u'MDA', u'MDG', u'ECU', u'SEN', u'NZL', u'MDV', u'ASM', u'CUW', u'FRA', u'LTU', u'RWA', u'ZMB', u'GMB', u'FRO', u'GTM', u'DNK', u'IMN', u'AUS', u'AUT', u'VEN', u'PLW', u'KEN', u'WSM', u'TUR', u'ALB', u'OMN', u'TUV', u'BRN', u'TUN', u'BRB', u'BRA', u'CIV', u'SRB', u'GNQ', u'USA', u'QAT', u'SWE', u'AZE', u'GNB', u'SWZ', u'TON', u'CAN', u'UKR', u'KOR', u'CAF', u'SVK', u'CYP', u'BIH', u'SGP', u'SOM', u'UZB', u'ERI', u'POL', u'KWT', u'GAB', u'CYM', u'EST', u'MWI', u'ESP', u'IRQ', u'SLV', u'MLI', u'IRL', u'IRN', u'ABW', u'PNG', u'PAN', u'SDN', u'SLB', u'MCO', u'ITA', u'JPN', u'KGZ', u'UGA', u'NCL', u'ARE', u'ARG', u'BHS', u'BHR', u'ARM', u'NRU', u'CUB']

def get_populations_from_wb(year, country_codes = countries_in_wb):
    total_population = "SP.POP.TOTL"
    dataset = api.get_dataset(total_population, country_codes, date=str(year))
    return {pycountry.countries.get(alpha_2=key).alpha_3:b.values()[0] for key, b in dataset.as_dict().iteritems()}


