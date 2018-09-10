import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from geonamescache import GeonamesCache
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

import country_helper_functions as chf

class world_map_chloropleth():

    title = ""
         
    def get_data_for_country_code(self,iso3):

        raise NotImplementedError

    def preprocess_data(self):

        return

    def process_chloropleth_data(self):
        
        self.preprocess_data()

        self.vals = {}
        self.failed_countries = []
        for iso3 in chf.country_iso3_list:
            try:
                self.vals[iso3] = self.get_data_for_country_code(iso3)
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
        # Borrowed from https://ocefpaf.github.io/python4oceanographers/blog/2015/08/24/choropleth/
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
                    iso3 = iso3 #Still want on map, just won't be colored correctly
                    if iso3 not in self.failed_isos:
                        self.failed_isos.append(iso3)
                    
                if iso3 in self.country_patches:
                    self.country_patches[iso3].append(Polygon(np.array(shape)))
                else: 
                    self.country_patches[iso3] =[Polygon(np.array(shape))]
        
        self.process_chloropleth_data()
        
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



