

import asyncio

from os import listdir, remove
from os.path import isfile, join

from pathlib import Path

from collections.abc import AsyncGenerator

from asyncio.exceptions import TimeoutError

from litestar import Litestar, get, post, Request
from litestar.plugins.htmx import HTMXPlugin, HTMXTemplate, ClientRedirect, ClientRefresh
from litestar.contrib.mako import MakoTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.response import Template, Redirect, File
from litestar.static_files import create_static_files_router
from litestar.datastructures import Cookie, State

from litestar.connection import ASGIConnection
from litestar.exceptions import NotFoundException

from litestar.response import ServerSentEvent, ServerSentEventMessage


# location of static files, for CSS and javascript
STATICFILES = Path(__file__).parent.resolve() / "static"

# location of template files
TEMPLATEFILES = Path(__file__).parent.resolve() / "templates"


# Dictionary of Global variables
PARAMETERS = {}


class CheckChange:
    """Iterate whenever a chart change occurs."""


    def __aiter__(self):
        return self

    async def __anext__(self):
        "Whenever there is a change, return a ServerSentEventMessage"
        global PARAMETERS
        mkchart = PARAMETERS['mkchart']
        while True:
            try:
                await asyncio.wait_for(mkchart.chart_event.wait(), timeout=5.0)
            except TimeoutError:
                # perhaps check for a stop flage here
                continue
            # a chart_event has occurred
            return ServerSentEventMessage(event="newchart")



# SSE Handler
@get(path="/check", sync_to_thread=False)
def check() -> ServerSentEvent:
    return ServerSentEvent(CheckChange())


def gotonotfound_error_handler(request: Request, exc: Exception) -> ClientRedirect|Redirect:
    """If a NotFoundException is raised, this handles it, and redirects
       the caller to the not found page"""
    global PARAMETERS
    basepath = PARAMETERS["basepath"]
    if basepath:
        redirectpath = basepath + "notfound"
    else:
        redirectpath = "/notfound"
    if request.htmx:
        return ClientRedirect(redirectpath)
    return Redirect(redirectpath)


@get("/notfound", sync_to_thread=False )
def notfound(request: Request) -> Template:
    "This is the not found page of your site"
    return Template("notfound.html")


@get("/")
async def publicroot(request: Request) -> ClientRedirect|Redirect:
    "This is the public root folder of your site"
    global PARAMETERS
    basepath = PARAMETERS["basepath"]
    if basepath:
        redirectpath = basepath + "chartpage.html"
    else:
        redirectpath = "/chartpage.html"
    if request.htmx:
        return ClientRedirect(redirectpath)
    return Redirect(redirectpath)


@get("/chartpage.html" )
async def chartpage(request: Request) -> Template:
    "This is the chart page of your site"
    global PARAMETERS
    mkchart = PARAMETERS['mkchart']
    if mkchart.chart is None:
        return Template("chartpage.html", context={"chart":None})
    return Template("chartpage.html", context={"chart":mkchart.chart.to_string()})


@get("/getchart" )
async def getchart(request: Request) -> Template:
    "This is just the chart"
    global PARAMETERS
    mkchart = PARAMETERS['mkchart']
    if mkchart.chart is None:
        return HTMXTemplate(None, template_str="<p>No chart generated</p>")
    return HTMXTemplate(None, template_str=mkchart.chart.to_string())



def make_app(basepath, mkchart):
    # Initialize the Litestar app with a Mako template engine and register the routes
    global PARAMETERS, STATICFILES, TEMPLATEFILES
    PARAMETERS['basepath'] = basepath
    PARAMETERS['mkchart'] = mkchart
     
    app = Litestar( path = basepath,
        route_handlers=[publicroot,
                        notfound,
                        chartpage,
                        check,
                        getchart,
                        create_static_files_router(path="/static", directories=[STATICFILES]),
                       ],
        exception_handlers={ NotFoundException: gotonotfound_error_handler},
        plugins=[HTMXPlugin()],
        template_config=TemplateConfig(directory=TEMPLATEFILES,
                                       engine=MakoTemplateEngine
                                      ),
        openapi_config=None
        )
    return app
