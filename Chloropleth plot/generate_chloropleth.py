import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
from IPython.display import display

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from geonamescache import GeonamesCache
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

import process_WB_data
import process_IEA2017_data
import country_helper_functions as chf

base_tmp_dir = os.path.join(os.getenv('TEST_TMPDIR', '/tmp'),'chloropleth')
if not os.path.exists(base_tmp_dir):
    os.makedirs(base_tmp_dir)

# To do - the data crunching functionality should be moved to the process IEA module. This should only handle plotting the data elegantly.
class chloropleth():
    def __init__(self):
        self.IEA_data = process_IEA2017_data.IEA_data()
        self.make_selection_dropdowns()

    def make_selection_dropdowns(self):
        self.product_selection = widgets.Dropdown(
            options=self.IEA_data.df1.Product.unique().tolist(),
            value='Total',
            description='Product:',
            disabled=False,
        )

        self.flow_selection = widgets.Dropdown(
            options=self.IEA_data.df1[self.IEA_data.df1.Product.isin([self.product_selection.value])].Flow.unique().tolist(),
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
            options=self.IEA_data.df1.Product.unique().tolist(),
            value='Total',
            description='Norm. Product:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        self.flow_norm_selection = widgets.Dropdown(
            options=self.IEA_data.df1[self.IEA_data.df1.Product.isin([self.product_selection.value])].Flow.unique().tolist(),
            value='Electricity output (GWh)',
            description='Norm. Flow:',
            disabled=False,
        )


        def set_flow_options(sender):
            new_options = self.IEA_data.df1[self.IEA_data.df1.Product.isin([self.product_selection.value])].Flow.unique().tolist()
            flow_selection.options = new_options
            if not flow_selection.value in new_options:
                flow_selection.value = new_options[0]

        self.product_selection.observe(set_flow_options)

        def set_norm_flow_options(sender):
            new_options = self.IEA_data.df1[self.IEA_data.df1.Product.isin([self.product_selection.value])].Flow.unique().tolist()
            flow_selection.options = new_options
            if not flow_selection.value in new_options:
                flow_selection.value = new_options[0]

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
            options=self.IEA_data.years,
            value=2015,
            description='Year:',
            disabled=False,
        )

    def display_dropdowns(self):
        display(self.year_selection,self.product_selection,self.flow_selection,self.norm_or_per_capita_selection,self.product_norm_selection,self.flow_norm_selection)
    
    def crunch_data(self):
        
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
    
        self.data = self.IEA_data.df1[np.logical_and(self.IEA_data.df1.Product.isin([self.product_var]),self.IEA_data.df1.Flow.isin([self.flow_var]))].filter(items=['Country',self.year])
        self.data.set_index('Country', inplace=True)
        self.data.at['Non-OECD Asia (including China)',self.year] = self.data.loc['Non-OECD Asia (including China)',self.year] - self.data.loc["People's Republic of China",self.year]
        self.data = self.data.rename({'Non-OECD Asia (including China)':'Non-OECD Asia'})
        
        if (self.calc_year != self.year) and self.per_capita:
            self.iea_region_pops = process_WB_data.update_wb_pops(self.year)
            self.calc_year = self.year
        
        if self.norm:
            self.norm_data = self.IEA_data.df1[np.logical_and(self.IEA_data.df1.Product.isin([self.product_norm_var]),self.IEA_data.df1.Flow.isin([self.flow_norm_var]))].filter(items=['Country',self.year])
            self.norm_data.set_index('Country', inplace=True)
            self.norm_data.at['Non-OECD Asia (including China)',self.year] = self.norm_data.loc['Non-OECD Asia (including China)',self.year] - self.norm_data.loc["People's Republic of China",self.year]
            self.norm_data = self.norm_data.rename({'Non-OECD Asia (including China)':'Non-OECD Asia'})
            
            for ind in self.data.index.tolist():
                self.data.at[ind,self.year] = self.data.loc[ind,self.year]/float(self.norm_data.loc[ind,self.year])
        
        if self.per_capita:
            for ind in self.iea_region_pops.keys():
                self.data.at[ind,self.year] = self.data.loc[ind,self.year]/self.iea_region_pops[ind]
            self.data = self.data.drop(['World', 'OECD Total','Non-OECD Total'])
            
        self.vals = {}
        self.failed_countries = []
        for iso3 in self.IEA_data.country_iso3_list:
            try:
                self.vals[iso3] = self.IEA_data.get_IEA_data_for_countries(self.data,iso3,self.year)
            except:
                self.failed_countries.append(iso3)
            
        cm = plt.get_cmap(self.cmap_scheme)
   
        if not self.min_max:
            if not self.norm:
                self.cmap = self.norm_cmap(self.vals.values(), cmap=cm)
            else:
                self.cmap = self.norm_cmap([0,1], cmap=cm)    
        else:
                self.cmap = self.norm_cmap(self.min_max, cmap=cm) 
        self.country_colors = {}
        for iso3,val in self.vals.iteritems(): 
            self.country_colors[iso3] = self.cmap.to_rgba(val)
         
    
    def norm_cmap(self,values, cmap, vmin=None, vmax=None):
        """
        Normalize and set colormap

        Parameters
        ----------
        values : Series or array to be normalized
        cmap : matplotlib Colormap
        normalize : matplotlib.colors.Normalize
        cm : matplotlib.cm
        vmin : Minimum value of colormap. If None, uses min(values).
        vmax : Maximum value of colormap. If None, uses max(values).

        Returns
        -------
        n_cmap : mapping of normalized values to colormap (cmap)

        """
        mn = vmin or min(values)
        mx = vmax or max(values)
        norm = Normalize(vmin=mn, vmax=mx)
        n_cmap = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        return n_cmap

    def plot_chloropleth(self,reset = False,cmap = 'BuGn',min_max=False):
         
        try: 
            self.mapfig
        except AttributeError:
            print 'Recalculating'
            reset = True
        self.cmap_scheme = cmap
        self.min_max = min_max
        
        if reset:
            
            self.calc_year = 0
            
            self.mapfig = plt.figure(figsize=(8, 5));

            self.mapax = self.mapfig.add_subplot(111, frame_on=False);
            self.ax_legend = self.mapfig.add_axes([0.27, 0.1, 0.5, 0.03]);
            self.cols = []

            self.m = Basemap(lon_0=0, projection='robin',ax=self.mapax)
            self.m.readshapefile("country_shapefiles/ne_10m_admin_0_countries_lakes", 'units', color='#444444', linewidth=.2)

            self.country_patches = {}
            self.failed_isos = []
            
            for info, shape in zip(self.m.units_info, self.m.units):
                iso3 = info['ADM0_A3']
                name = info['NAME']
                try:
                    iso3 = chf.match_country_by_code_or_name(iso3,name)
                except:
                    iso3 =iso3 #Still want on map, just won't be colored correctly
                    if iso3 not in self.failed_isos:
                        self.failed_isos.append(iso3)
                    
                if iso3 in self.country_patches:
                    self.country_patches[iso3].append(Polygon(np.array(shape)))
                else: 
                    self.country_patches[iso3] =[Polygon(np.array(shape))]
        
        self.crunch_data()
        
        # Following http://ramiro.org/notebook/basemap-choropleth/  
        self.mapfig.suptitle(self.title, fontsize=14, y=.95)

        for col in self.cols:
            try:
                col.remove()
            except:
                pass
        for iso3, patches in self.country_patches.iteritems():
            pc = PatchCollection(patches)
            if iso3 in self.country_colors:
                pc.set_facecolor(self.country_colors[iso3])
            else:
                 pc.set_facecolor('#dddddd')
            self.cols.append(self.mapax.add_collection(pc))

        # Draw color legend.
        self.cmap.set_array([]) # can be an empty list
        def fmt(x, pos):
            a, b = '{:.1e}'.format(x).split('e')
            b=int(b)
            return r'${}\!\times\!10^{{{}}}$'.format(a,b)
        if self.norm:
            self.cb = self.mapfig.colorbar(self.cmap, ax=self.mapax,cax=self.ax_legend, orientation='horizontal');
        else:
            self.cb = self.mapfig.colorbar(self.cmap, ax=self.mapax,cax=self.ax_legend, orientation='horizontal'
                                   ,format=mpl.ticker.FuncFormatter(fmt));

        self.cb.ax.tick_params(labelsize=7) 
#         plt.setp(self.cb.ax.get_xticklabels(), rotation=30,horizontalalignment ='right')
        display(self.mapfig)



