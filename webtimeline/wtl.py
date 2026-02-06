
import asyncio

import uvicorn

import minilineplot

from .web.app import make_app


class WebTimeLine:

    def __init__(self, host='localhost', port=8000, basepath=None, hours=4, height=600, width=800, title="", description=""):
        self._host = host
        self._port = port
        self._queue = asyncio.Queue()
        self._mkchart = MakeChart(hours=hours, height=height, width=width, title=title, description=description, queue = self._queue)
        self._server = None

        # ensure basepath is either None, or a string with leading and tailing '/' characters
        if basepath:
            basepath = basepath.strip("/. ")
        if basepath:
            self._basepath = f"/{basepath}/"
        else:
            self._basepath = None



    async def serve(self, tg):
        app = make_app(self._basepath, self._mkchart)
        config = uvicorn.Config(app=app, host=self._host, port=self._port, log_level="error")
        self._server = uvicorn.Server(config)
        tg.create_task( self._server.serve() )
        tg.create_task( self._mkchart.run() )


    async def putpoint(self, t, v):
        "Put a point timestamp, value"
        item = (t,v)
        await self._queue.put(item)

    def set_colors(self,
                   backcol = "white",      # The background colour of the whole image
                   gridcol = "grey",       # Color of the chart grid
                   axiscol = "black",      # Color of axis, title and description
                   chartbackcol = "white", # Background colour of the chart
                   linecol = "blue"        # Color of the line being plotted
                   ):
        self._mkchart.set_colors(backcol, gridcol, axiscol, chartbackcol, linecol)


    def set_title(self, title):
        self._mkchart.set_title(title)

    def set_description(self, description):
        self._mkchart.set_description(description)

    def set_y_axis(self, ymin, ymax, yintervals, yformat):
        """If this is not called, an automatic y scaling will be used.
           If it is called, then these values will be set, however if any y point
           exceeds the values, then the chart will revert to auto-scaling.
           If you wish to revert to autoscaling, call this with None values."""
        self._mkchart.set_y_axis(ymin, ymax, yintervals, yformat)


class MakeChart:

    def __init__(self, hours, height, width, title, description, queue):
        self.hours = hours
        self.height = height
        self.width = width
        self.title = title
        self.description=description
        self.queue = queue
        self.backcol = "white"
        self.gridcol = "grey"
        self.axiscol = "black"
        self.chartbackcol = "white"
        self.linecol = "blue"
        self.points = []
        self.chart = None

        self.ymin = None
        self.ymax = None
        self.yintervals = None
        self.yformat = None

        # this event is triggered when a chart event occurs
        self.chart_event = asyncio.Event()

    async def run(self):
        "Creates the chart when a new point added"
        while True:
            item = await self.queue.get()
            self.points.append(item)
            last_t = item[0]
            first_t = self.points[0][0]
            tspan = last_t - first_t
            plotted_span = self.hours * 3600
            if first_t < last_t - plotted_span:
                self.points.pop(0)
            self.make_chart()


    def make_chart(self):
        if len(self.points)<2:
            return
        line = minilineplot.Line(values=self.points,
                                 color = self.linecol)
        self.chart = minilineplot.Axis(lines=[line],
                                       imagewidth=self.width,
                                       imageheight=self.height,
                                       title = self.title,
                                       description = self.description,
                                       gridcol = self.gridcol,
                                       axiscol = self.axiscol,
                                       chartbackcol = self.chartbackcol,
                                       backcol = self.backcol)
        ymax = max(p[1] for p in self.points)
        ymin = min(p[1] for p in self.points)
        if self.ymin is None or self.ymax is None or self.yformat is None or self.yintervals is None :
            self.chart.auto_y()
        elif ymin<self.ymin or ymax>self.ymax:
            self.chart.auto_y()
        else:
            self.chart.ymax = self.ymax
            self.chart.ymin = self.ymin
            self.chart.yintervals = self.yintervals
            self.chart.yformat = self.yformat
        self.chart.auto_time_x(hourspan = self.hours)
        # flag a chart event
        self.chart_event.set()
        self.chart_event.clear()


    def set_colors(self, backcol, gridcol, axiscol, chartbackcol, linecol):
        self.backcol = backcol
        self.gridcol = gridcol
        self.axiscol = axiscol
        self.chartbackcol = chartbackcol
        self.linecol = linecol
        self.make_chart()


    def set_title(self, title):
        self.title = title
        self.make_chart()


    def set_description(self, description):
        self.description = description
        self.make_chart()

    def set_y_axis(self, ymin, ymax, yintervals, yformat):
        """If this is not called, an automatic y scaling will be used.
           If it is called, then these values will be set, however if any y point
           exceeds the values, then the chart will revert to auto-scaling.
           If you wish to revert to autoscaling, call this with None values."""
        self.ymin = ymin
        self.ymax = ymax
        self.yintervals = yintervals
        self.yformat = yformat
        self.make_chart()




        


