import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import pandas as pd

from .Preparedata import PrepareData

class LineGraph(PrepareData):
    
    """
    The LineGraph class produces a Plotly figure that is well-formatted 
    and well labeled for a time series data analysis
    """
    def __init__(self,file_name, x_label, y_label, title, description):
        
        """
        Initialize object attributes:
            x_label (string)
            y_label
            title (string) is the title of the figure
            text (string) represents the main highlights of the figure
            y_pchange (string, percentage) represents the percentage change from previous year
            mean (float) is the mean value of the dataset
        """
        PrepareData.__init__(self)
        
        self.df, self.x, self.y, self.y_pchange, self.mean = self.read_data_file(file_name)
        
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.text = description

        
        # Set font for figure axis labels
        self.lab_axes_dict = dict(family="sans-serif",
                             size=16,
                             color="#B1B1B1"
                             )
        
        # Set font for figure title
        self.lab_title_dict = dict(family="sans-serif",
                             size=18,
                             color="#000000"
                             )
        
      
        # Set layout of all the annotations that appears on the figure    
        self.layout = go.Layout(
                                annotations = [
                                go.layout.Annotation(
                                    x=-0.1,
                                    y=1.1,
                                    showarrow=False,
                                    text=self.title,
                                    xref="paper",
                                    yref="paper",
                                    font=self.lab_title_dict
                                    ),
                                go.layout.Annotation(
                                    x=0,
                                    y=-0.175,
                                    showarrow=False,
                                    text=self.x_label,
                                    xref="paper",
                                    yref="paper",
                                    font=self.lab_axes_dict
                                    ),
                                go.layout.Annotation(
                                    x=-0.1,
                                    y=1.0,
                                    yanchor='top',
                                    showarrow=False,
                                    text=self.y_label,
                                    xref="paper",
                                    yref="paper",
                                    font=self.lab_axes_dict
                                    ),
                                # labeling the left_side of the figure
                                go.layout.Annotation(
                                    xref='paper', 
                                    x=-0.01, 
                                    y=self.y[0],
                                    xanchor='right', 
                                    yanchor='middle',
                                    text='{:,}'.format(int(self.y[0])),
                                    font=dict(
                                        family='sans-serif',
                                        size=16,
                                        color = 'cornflowerblue'),
                                    showarrow=False),
                                    # labeling the right_side of the figure
                                    go.layout.Annotation(dict(xref='paper', x=1.01, y=self.y[9],
                                        xanchor='left', yanchor='middle',
                                        text='{:,}'.format(int(self.y[9])),
                                        font=dict(
                                            family='sans-serif',
                                            size=16,
                                            color = 'royalblue'),
                                        showarrow=False)),
                                    # labeling the line for the average
                                    go.layout.Annotation(dict(xref='paper', x=1.01, y=np.mean(self.y),
                                                              xanchor='left', yanchor='middle',
                                                              text='avg ' + '{:,}'.format(int(np.mean(self.y))),
                                                              font=dict(
                                                                  family='sans-serif',
                                                                  size=15,
                                                                  color = 'lightsteelblue'),
                                                              showarrow=False)),
                                    # Position the figure description box
                                    go.layout.Annotation(
                                        text=self.text,
                                        align='left',
                                        showarrow=False,
                                        xref='paper',
                                        yref='paper',
                                        x=1.5,
                                        y=0.8
                                    )],
            xaxis = dict(dtick = 1, zeroline=True, linecolor='#D2D2D2'),
            yaxis = dict(visible = False),
            plot_bgcolor='rgba(0,0,0,0)',
            margin = dict(t = 90, r = 300, b = 80, l = 180)
        )
    
    
    def line_plot(self):
        
        '''
        Function to output the figure of a time series using plotly graph_objs library.
        
        Args:
            None
        
        Returns:
            fig
        '''

        x = self.x
        y = self.y

        fig = go.Figure(
            data = [go.Scatter(
                mode = 'lines+markers',
                x = x,
                y = y,
                marker_color = 'royalblue',
                line = dict(width = 3),
                text = self.y_pchange,
                hoverinfo = 'x+y+text')],
            layout = self.layout
        )

        # Add a line for the average overtime
        fig.add_hline(y=self.mean,line_dash="dash", line_color="lightsteelblue")

        fig.update_layout(showlegend=False)

        return fig
            
            
    def save_fig_png(self, name):
        
        '''
        Function to output save figure as png using plotly io library.
        
        Args:
            name of the figure
        
        Returns:
            None
        '''
        
        fig = self.line_plot()
        
        pio.write_image(fig, f'{name}.png', width=1000, height=450, scale=3)
        
    def save_fig_html(self, name):

        '''
        Function to output save figure as html using plotly io library.

        Args:
            name of the figure

        Returns:
            None
        '''

        fig = self.line_plot()

        fig.write_html(f'{name}.html')

        
        





