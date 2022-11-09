import pandas as pd
import json
import datetime as dt
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import colors as clr

#TODO:
# -interact w database
# -seaborn instead of matplotlib?
# -grafana

def make_bar_plot(x_values,y_values,title,x_label, y_label):
    
    #normalize y_values and create colormap
    my_norm = clr.Normalize(vmin = min(y_values), vmax = max(y_values))
    my_cmap = mpl.cm.get_cmap('Reds') 
    plt.bar(x_values, y_values, width = 1, color = my_cmap(my_norm(y_values)), edgecolor= "#5F3B54")
    
    # Set chart title and label axes.
    plt.title(title, fontsize=20)
    plt.xlabel(x_label, fontsize=16)
    plt.ylabel(y_label, fontsize=16)
    
    # Set size of tick labels.
    plt.tick_params(axis='both', which='major', labelsize=12)
    
    plt.show()


def run():
    x_values = [1, 2, 3, 4, 5]
    y_values = [1, 4, 9, 16, 25]
    make_bar_plot(x_values, y_values, 'Squares', 'Int', 'Sq')
    
if __name__ == "__main__":
    run()