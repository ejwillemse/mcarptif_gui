# MCARPTIF GUI

This repository contains a Python 3.7.0 based GUI that shows how waste collection routes can be generated and visualised for two adjacent collection areas. The areas are Watville and Actonville, in South Africa.

The GUI was originally developed in 2013; that it still works says more about python than my coding. Getting it up-and-running is a bit troublesome and only verified on macOS Mojave. The GUI makes use of tkinter, and there is a nasty bug, described [here](https://stackoverflow.com/questions/57400301/how-to-fix-tkinter-every-code-with-gui-crashes-mac-os-with-respring), in later python versions where it instantly crashes Macs when launched.

The heuristics used to generate the routes are prequels to the MCARPTIF algorithms from <https://github.com/ejwillemse/mcarptif>.

## Setup

The easiest way to get it up and running is via command-line/terminal, and to use [Anaconda](https://www.anaconda.com/distribution/) to setup a Python 3.7.0 virtual environment. After installing anaconda, navigate to the cloned repository and create and activate a new virtual environment:

```
$ conda create --name mcarptif_gui_370  python=3.7.0
```

Follow the prompts and then activate the environment:

```
$ conda activate mcarptif_gui_370
```

Next, install all the project dependencies via the included `requirements.txt` file. Note that this requires `pip`

```
$ pip install -r requirements.txt
```

We can now launch the GUI. Navigate to the GUI folder and then launch `d_WacoPlanner_GUI.py`:

```
$ cd GUI
$ python d_WacoPlanner_GUI.py
```

If your computer crashes, chances are you're using a python version later than 3.7.0, hence why the python 3.7.0 virtual environment is required.

## Using the GUI

Using the GUI is straightforward. Just make sure to leave the terminal session active in the background. You'll be able to see the heuristics at work in-it.

![](demo_gifs/gui_demo1.gif)

The image above shows the GUI with the terminal window placed underneath it. The depot is the black node to the left, and the landfill site the red one to the right.

Select an area to generate routes for at the top, change the collection parameters, and click on `Generate Collection Routes`. The routes will then show on the map, and each route and subroute can be selected and viewed with some basic operational info, like total distance travelled, and estimated service cost. There is also an option to generate routes to service both areas by the same vehicles; this requires fewer vehicles.

You can change the parameters and click on `Generate Collection Routes` to see their impact. `Activate Local Search` will produce better routes but takes some time to run.

The next image shows what happens if we increase vehicle capacity and work day lenght input parameters:

![](demo_gifs/gui_demo2.gif)

