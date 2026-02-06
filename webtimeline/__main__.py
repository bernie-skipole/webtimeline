import asyncio, time, random

from . import WebTimeLine


### This creates an example web service, with random measurements every ten seconds

## Create WebTimeLine object
tline =  WebTimeLine(host='localhost', port=8000, basepath=None, hours=1, title="My Title", description="Data display")

# set a y axis, lowest value 0.0
#               highest 80.0
#               with four intervals up the axis (five values shown at grid lines)
#               and axis numbers printed with one decimal point

tline.set_y_axis(ymin=0.0, ymax=80.0, yintervals=4, yformat=".1f")

async def my_function(tline):
    "Create data and send it using tline.putpoint()"
    while True:
        value = random.uniform(30, 70)   # random value used here
        await tline.putpoint(time.time(), value)
        await asyncio.sleep(10) # pause 10 seconds between readings

## create two tasks, one runs the web server, one gathers data

async def runchart():
    async with asyncio.TaskGroup() as tg:
        tg.create_task( tline.serve(tg) )
        tg.create_task( my_function(tline) )
        print("Now serving at localhost:8000")



def main():
    "Run the program"
    asyncio.run(runchart())


if __name__ == "__main__":
    # And run main
    main()
