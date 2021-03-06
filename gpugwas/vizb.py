#!/opt/conda/envs/rapids/bin/python
"""
Pre-reqs:
---------
/opt/conda/envs/rapids/bin/pip install bokeh
"""

import cudf
import cupy

from  bokeh.io.export import export_png

from bokeh.plotting import figure
from bokeh.models.tickers import FixedTicker
from bokeh.io import output_notebook, push_notebook, show

output_notebook()


def show_qq_plot(df, x_axis, y_axis, title="QQ", 
                 save_to=None, x_max=None, y_max=None):

    x_values = cupy.fromDlpack(df[x_axis].to_dlpack())
    y_values = cupy.fromDlpack(df[y_axis].to_dlpack())

    x_values = -cupy.log10(x_values)
    y_values = -cupy.log10(y_values)

    if x_max is None:
        x_max = cupy.max(x_values).tolist()
    if y_max is None:
        y_max = cupy.max(y_values).tolist()

    if y_max == cupy.inf:
        print("Please pass y_max. Input contains inf.")
        return
    if x_max == cupy.inf:
        print("Please pass x_max. Input contains inf.")
        return

    qq_fig = figure(x_range=(0, x_max), 
                    y_range=(0, y_max),
                    title=title)
    qq_fig.circle(x_values.get(), y_values.get(), size=1)
    qq_fig.line([0, x_max], [0, y_max], line_color='orange', line_width=2)

    if save_to:
        export_png(qq_fig, filename=save_to)
    else:
        qq_handle = show(qq_fig, notebook_handle=True)
        push_notebook(handle=qq_handle)
    
    return qq_fig


def show_manhattan_plot(df, group_by, x_axis, y_axis, 
                        title='Manhattan Plot',
                        save_to=None):
    chroms = df[group_by].unique().to_array()
    
    plot_width = len(chroms) * 50

    manhattan_fig = figure(title=title)
    manhattan_fig.xaxis.axis_label = 'Chromosomes'
    manhattan_fig.yaxis.axis_label = '-log10(p)'

    manhattan_fig.xaxis.ticker = FixedTicker(ticks=[t for t in chroms])

    start_position = 0.5
    for chrom in chroms:
        query = '%s == %s' % (group_by, chrom)
        cdf = df.query(query)

        x_array = cupy.fromDlpack(cdf[x_axis].to_dlpack())  + start_position
        y_array = -cupy.log10(cupy.fromDlpack(cdf[y_axis].to_dlpack()))

        manhattan_fig.circle(
            x_array.get(),
            y_array.get(),
            size=2, color='orange' if (start_position - 0.5) % 2 == 0 else 'gray', alpha=0.5)

        start_position += 1


    if save_to:
        export_png(manhattan_fig, filename=save_to)
    else:
        manhattan_handle = show(manhattan_fig, notebook_handle=True)
        push_notebook(handle=manhattan_handle)
    
    return manhattan_fig