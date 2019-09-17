"""
Plot diagrams using arbitrary time series data of the form:

time,category,subcategory,measurement
2019-02-17,pytest,coverage,0
2019-03-03,pytest,coverage,78
2019-03-10,pylint,score,8.63
2019-03-17,pylint,score,8.63
2019-02-17,DAST,coverage,2
2019-03-03,DAST,coverage,2
2019-03-03,DAST,untriaged,72
2019-03-10,DAST,untriaged,72
2019-03-17,Dependency Check,critical,720

This was created to consolidate counts of security tools vulnerability
outputs into simple time series charts, where category is a tool and
subcategory is a type of finding.  However, it can be used for any
arbitrary category and subcategory timeseries you like.

"""
import argparse
import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from pandas import Series
from pandas.plotting import register_matplotlib_converters
import itertools
from math import ceil
 
def setup_plot_style():
    register_matplotlib_converters()
    plt.rcParams.update(plt.rcParamsDefault)
    plt.style.use('ggplot')
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 9
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 8

def trend_line_and_x(l):
    # fit polynomial of degree 1 :)
    x = [i for i in range(len(l))]
    f = np.polyfit(x, l, 1)
    return np.poly1d(f), x
    
if __name__ == "__main__":
     parser = argparse.ArgumentParser(description="Plot a series of chart from timeseries data")
     parser.add_argument("--cols",type=int,default=2,
                         help="number image columns (2 by default)")
     parser.add_argument("--category",type=str, default="category",
                         help="title of category column (e.g. tool)")
     parser.add_argument("--subcategory",type=str, default="subcategory",
                         help="title of subcategory column (e.g. tool)")
     parser.add_argument("--time",type=str, default="time",
                         help="title of time column (e.g. datetime). String must be convertible by pandas.to_datetime")
     parser.add_argument("--measurement",type=str, default="measurement",
                         help="title of measurement column (e.g. numeric_reading).")

     parser.add_argument("infile",type=argparse.FileType("r"),nargs="?",default=sys.stdin,
                         help="read input from provided csv file (stdin by default)")
     parser.add_argument("outfile",
                         help="save result as csv in provided file (stdout by default)")
     setup_plot_style()
     args = parser.parse_args()
     df = pd.read_csv(args.infile)
     # TODO: allow for no-headers input
     cat = args.category
     sub = args.subcategory
     mes = args.measurement
     time = args.time     
     df.set_index([cat,sub],inplace=True)
     df.sort_values(time,inplace=True)

     fig = plt.figure(1)
     s_i = 1
     rows = ceil(len(np.unique(df.index.get_level_values(cat)))/args.cols)
     for t in np.unique(df.index.get_level_values(cat)):
         plt.subplot(rows,args.cols,s_i)
         plt.title(t, fontsize=12)
         plt.xticks(rotation=10)
         for m in np.unique(df.loc[t,:].index.get_level_values(sub)):
            data = df.loc[t,m]
            data[time] = pd.to_datetime(data[time])
            plt.plot(data[time].tolist(),data[mes].tolist())
         plt.legend(np.unique(df.loc[t,:].index.get_level_values(sub)))
         s_i +=1
     plt.subplots_adjust(top=.90, bottom=0.08, left=0.10, right=0.95, hspace=.43,wspace=0.35)
     plt.gcf().set_size_inches(16,9)
     plt.savefig(args.outfile,dpi=300)
