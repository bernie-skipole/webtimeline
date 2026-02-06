

from .wtl import WebTimeLine


# Usage

# Create instance of WebTimeLine class

# tline =  WebTimeLine(host='localhost', port=8000, basepath=None, hours=4, title="My Title")

# hours should be between 1 and 48
# a task tline.serve(tg) should be created to run the web server, tg being a taskgroup
# tline.putpoint(t, v) should be awaited to insert points


####### Example

# install dependencies
# pip install litestar[standard]
# pip install mako
# pip install minilineplot


######### and the script would be something like :


# import asyncio, time
#
# from webtimeline import WebTimeLine
#
## Create WebTimeLine object
# tline =  WebTimeLine(host='localhost', port=8000, basepath=None, hours=4, title="My Title")
#
# async def my_function(tline):
#     while True:
#         # Get value from somewhere ....
#         # and puts the measurement into the plot
#         await tline.putpoint(time.time(), v)
#         await asyncio.sleep(10) # pause between readings, and allow webserver to work
#
#
## create two tasks, one runs the web server, one runs my_function(tline) gathering data
#
# async def runchart():
#     async with asyncio.TaskGroup() as tg:
#         tg.create_task( tline.serve(tg) )
#         tg.create_task( my_function(tline) )
#
## And run the loop
# asyncio.run(runchart())




