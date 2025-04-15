# examples
import pandas as pd
import os 
import sys
sys.path.append(os.path.abspath(os.getcwd()))
from plot import *

###### example timeline data
df = pd.read_csv('examples/data/timeline_anon.csv')
chart = plot_timeline(df)
chart.save('examples/figures/timeline.html')

###### example simple event timeline
df = pd.read_csv('examples/data/simple_timeline_anon.csv')
chart = plot_simple_timeline(df.reset_index(drop=True),
                                date='event_days',date_title = 'days from treatment start', 
                                colour = "event_type",
                                palette = ["#138086",'#DC8665',"black"],
                                shape='event',
                                tooltip=list(df.keys()),
                                order ='(datum.treatment_classification_num)',
                                title="ARM A")
chart.configure_axis(labelFontSize=14,titleFontSize=18
        ).configure_title(fontSize=20, 
        anchor="middle").configure_legend(titleColor='black', 
        titleFontSize=16,labelFontSize=16).interactive()
chart.save('examples/figures/simple_timeline.html')

###### example KaplanMeier
df = pd.read_csv('examples/data/km_anon.csv')
chart = plot_kaplanmeier(df,colour='Treatment_arm',palette=["#4190B1","orange"],ci=True,title='Overall Survival')
chart.save('examples/figures/km.html')

###### example Swimmer plot
df = pd.read_csv('examples/data/swimmer_anon.csv')
chart = plot_swimmer(df,"ARM A",legend=False,
                     colors_outcome=['gray','red','orange','orange','lightblue']).configure_axis(labelFontSize=18,titleFontSize=18
                ).configure_title(fontSize=20, 
                anchor="middle").configure_legend(titleColor='black', 
                titleFontSize=16,labelFontSize=16).interactive()
chart.save('examples/figures/swimmer.html')
