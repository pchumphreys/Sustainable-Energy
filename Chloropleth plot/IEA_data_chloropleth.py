import ipywidgets as widgets
import numpy as np

from chloropleth import world_map_chloropleth
from IEA_2017_data import IEA_handler
import WorldBank_data

class IEA_chloropleth(world_map_chloropleth,IEA_handler):

    def __init__(self, force_reload = False):
        IEA_handler.__init__(self,force_reload = force_reload)
        self.make_selection_dropdowns()

    def make_selection_dropdowns(self):
        self.product_selection = widgets.Dropdown(
            options=self.IEA_data.Product.unique().tolist(),
            value='Total',
            description='Product:',
            disabled=False,
        )

        self.flow_selection = widgets.Dropdown(
            options=self.IEA_data[self.IEA_data.Product.isin([self.product_selection.value])].Flow.unique().tolist(),
            value='Electricity output (GWh)',
            description='Flow:',
            disabled=False,
        )

        self.norm_or_per_capita_selection = widgets.RadioButtons(
            options=['None', 'Normalise', 'Per Capita'],
            value='None',
            description='Options: ',
            disabled=False,
        )


        self.product_norm_selection = widgets.Dropdown(
            options=self.IEA_data.Product.unique().tolist(),
            value='Total',
            description='Norm. Product:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self.flow_norm_selection = widgets.Dropdown(
            options=self.IEA_data[self.IEA_data.Product.isin([self.product_selection.value])].Flow.unique().tolist(),
            value='Electricity output (GWh)',
            description='Norm. Flow:',
            disabled=False,
        )


        def set_flow_options(sender):
            new_options = self.IEA_data[self.IEA_data.Product.isin([self.product_selection.value])].Flow.unique().tolist()
            self.flow_selection.options = new_options
            if not self.flow_selection.value in new_options:
                self.flow_selection.value = new_options[0]

        self.product_selection.observe(set_flow_options)

        def set_norm_flow_options(sender):
            new_options = self.IEA_data[self.IEA_data.Product.isin([self.product_selection.value])].Flow.unique().tolist()
            self.flow_norm_selection.options = new_options
            if not self.flow_norm_selection.value in new_options:
                self.flow_norm_selection.value = new_options[0]

        self.product_norm_selection.observe(set_norm_flow_options)

        def set_additional_options(sender):
            if self.norm_or_per_capita_selection.value != 'Normalise':
                self.flow_norm_selection.disabled = True
                self.product_norm_selection.disabled = True
            else:
                self.flow_norm_selection.disabled = False
                self.product_norm_selection.disabled = False

        self.norm_or_per_capita_selection.observe(set_additional_options)


        self.year_selection = widgets.Dropdown(
            options=self.years,
            value=2015,
            description='Year:',
            disabled=False,
        )

    def display_dropdowns(self):
        display(self.year_selection,self.product_selection,self.flow_selection,self.norm_or_per_capita_selection,self.product_norm_selection,self.flow_norm_selection)
    
    def preprocess_data(self):
        
        if self.norm_or_per_capita_selection.value == 'Normalise':
            self.norm = True
            self.per_capita = False
        elif self.norm_or_per_capita_selection.value == 'Per Capita':
            self.norm = False
            self.per_capita = True
        else:
            self.norm = False
            self.per_capita = False
            
        self.year = self.year_selection.value
        self.product_var = self.product_selection.value
        self.flow_var = self.flow_selection.value
        self.product_norm_var = self.product_norm_selection.value
        self.flow_norm_var = self.flow_norm_selection.value
        
        self.title = self.product_var + ', ' + self.flow_var + ' {}'.format(self.year)
        if self.norm:
            self.title += '\n Normalised by ' + self.product_norm_var + ', ' + self.flow_norm_var
        elif self.per_capita:
            self.title += ' per capita'
    
        self.plot_data = self.IEA_data[np.logical_and(self.IEA_data.Product.isin([self.product_var]),self.IEA_data.Flow.isin([self.flow_var]))].filter(items=['Country',self.year])
        self.plot_data.set_index('Country', inplace=True)
        self.plot_data.at['Non-OECD Asia (including China)',self.year] = self.plot_data.loc['Non-OECD Asia (including China)',self.year] - self.plot_data.loc["People's Republic of China",self.year]
        self.plot_data = self.plot_data.rename({'Non-OECD Asia (including China)':'Non-OECD Asia'})
        
        if (self.calc_year != self.year) and self.per_capita:
            self.iea_region_pops = self.get_country_pops()
            self.calc_year = self.year
        
        if self.norm:
            self.norm_data = self.IEA_data[np.logical_and(self.IEA_data.Product.isin([self.product_norm_var]),self.IEA_data.Flow.isin([self.flow_norm_var]))].filter(items=['Country',self.year])
            self.norm_data.set_index('Country', inplace=True)
            self.norm_data.at['Non-OECD Asia (including China)',self.year] = self.norm_data.loc['Non-OECD Asia (including China)',self.year] - self.norm_data.loc["People's Republic of China",self.year]
            self.norm_data = self.norm_data.rename({'Non-OECD Asia (including China)':'Non-OECD Asia'})
            
            for ind in self.plot_data.index.tolist():
                if self.norm_data.loc[ind,self.year] != 0:    
                    self.plot_data.at[ind,self.year] = self.plot_data.loc[ind,self.year]/float(self.norm_data.loc[ind,self.year])
                else: self.plot_data.at[ind,self.year] = 0
        if self.per_capita:
            for ind in self.iea_region_pops.keys():
                self.plot_data.at[ind,self.year] = self.plot_data.loc[ind,self.year]/self.iea_region_pops[ind]
            self.plot_data = self.plot_data.drop(['World', 'OECD Total','Non-OECD Total'])
      
    def get_data_for_country_code(self,iso3):
        try:
            region = self.iea_country_codes_to_named_region[iso3]
        except:
            raise ValueError("Couldn't find country data for %s" % self.iea_country_codes_to_named_region[iso3])
        return self.plot_data.loc[region,self.year]


    def return_sum_of_all_in(self,list_of_countries,pop_key):
        total = 0.0
        for country in list_of_countries:
            if country in pop_key:
                if pop_key[country] is not None:
                    total += pop_key[country]
        return total
                
    def get_country_pops(self):
        all_country_pops = WorldBank_data.get_populations_from_wb(self.year)
        iea_region_pops = {country:all_country_pops[key] for key,country in self.iea_specified_country_codes.iteritems()}
        iea_region_pops['Middle East'] = self.return_sum_of_all_in(self.middle_eastern_country_codes,all_country_pops)
        iea_region_pops['Non-OECD Europe and Eurasia'] = self.return_sum_of_all_in(self.non_OECD_Eurasian_country_codes,all_country_pops)
        iea_region_pops['Non-OECD Asia'] =  self.return_sum_of_all_in(self.non_OECD_asia_country_codes,all_country_pops)
        iea_region_pops['Africa'] = self.return_sum_of_all_in(self.african_country_codes,all_country_pops)
        iea_region_pops['Non-OECD Americas'] = self.return_sum_of_all_in(self.non_oecd_americas_country_codes,all_country_pops)
        return iea_region_pops

