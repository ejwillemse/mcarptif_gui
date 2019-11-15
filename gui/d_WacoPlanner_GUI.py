from tkinter import *
from tkinter import ttk
import c_WacoPlanner_v001 as solver
from PIL import ImageTk
from copy import deepcopy

root = Tk()
root.title("WaCo Optimisation Tool - Actonville and Watville demo")

#    - Waste in area
#    - Number of street segments
#    - Number of required street segments
# Initialise fleet setup
#    - Number of available vehicles
#    - Vehicle capacity
#    - Available working time

areastats = {}
areastats['Actonville'] =           {'waste':'41580','nedges':'654','nreqges':'151','wasteperhouse':'28','households':'1485',
                                    'nroues':'5','cap':'19','maxroute':'8','dumptime':'15','compactratio':'4','effectivecap':'10148',
                                    'cost':'25'}

areastats['Watville'] =             {'waste':'99232','nedges':'654','nreqges':'250','wasteperhouse':'28','households':'3544',
                                    'nroues':'5','cap':'19','maxroute':'8','dumptime':'15','compactratio':'4','effectivecap':'10148',
                                    'cost':'25'}

areastats['ActonvilleWatville'] =   {'waste':'140812','nedges':'654','nreqges':'401','wasteperhouse':'28','households':'5029',
                                    'nroues':'5','cap':'19','maxroute':'8','dumptime':'15','compactratio':'4','effectivecap':'10148',
                                    'cost':'25'}

area_network_path = {}
area_network_path['Actonville'] = 'Files/Network_Maps/Actonville_Full_Network.png'
area_network_path['Watville'] = 'Files/Network_Maps/Watville_Full_Network.png'
area_network_path['ActonvilleWatville'] = 'Files/Network_Maps/ActonvilleWatville_Full_Network.png'

area_problem_info = {}
area_problem_info['Actonville'] = 'Files/Input_Data/Actonville_pickled.dat'
area_problem_info['Watville'] = 'Files/Input_Data/Watville_pickled.dat'
area_problem_info['ActonvilleWatville'] = 'Files/Input_Data/ActonvilleWatville_pickled.dat'

area_route_library = {}
area_route_library['Actonville'] = {}
area_route_library['Watville'] = {}
area_route_library['Actonville'] = {}
current_list_area = 'Actonville'

route_names = ()
croutes = StringVar(value=route_names)

route_files = {}
route_files['Actonville'] = []
route_files['Watville'] = []
route_files['ActonvilleWatville'] = []

area_route_tree = {}
area_route_tree['Actonville'] = {}
area_route_tree['Watville'] = {}
area_route_tree['ActonvilleWatville'] = {}

current_area_route_tree = []

route_files_map = {}
route_files_map['Actonville'] = {}
route_files_map['Watville'] = {}
route_files_map['ActonvilleWatville'] = {}

fleetSize = StringVar()
vehicleCap = StringVar()
dayLength = StringVar()

# State variables
area = StringVar()
area_waste = StringVar()
area_arcs = StringVar()
area_reqarcs = StringVar()
wasteperhouse = StringVar()

area_vehicles = StringVar()
area_cap = StringVar()
area_cap2 = StringVar()
area_compac = StringVar()
area_dumptime = StringVar()
area_maxtrip = StringVar()
area_cost = StringVar()
local_search_flag = BooleanVar()
image = PhotoImage()
route_names_d = {}
tree_exists = False
tree_ids = []
route_tree_dict = {}
infofile = None
info = None
area_cost = StringVar()

old_waste_adjust = {'Actonville':10,'Watville':10,'ActonvilleWatville':10}

areasolved = {'Actonville':False, 'Watville': False, 'ActonvilleWatville':False}

# Called when an area is selected via the radio button
def showareastats(*args):
    global file_name_new
    global network_canvas
    global img_network
    global area_key
    global wasteperhouse
    global area_cap2
    global area_dumptime
    global area_compac
    global area_cost
    global old_waste_adjust
    area_key = area.get()

    area_waste.set(areastats[area_key]['waste'])
    area_arcs.set(areastats[area_key]['nedges'])
    area_reqarcs.set(areastats[area_key]['nreqges'])
    wasteperhouse.set(areastats[area_key]['wasteperhouse'])
    
    area_vehicles.set(areastats[area_key]['nroues'])
    area_cap.set(areastats[area_key]['cap'])
    area_maxtrip.set(areastats[area_key]['maxroute'])
    area_cap2.set(areastats[area_key]['effectivecap'])
    area_dumptime.set(areastats[area_key]['dumptime'])
    area_compac.set(areastats[area_key]['compactratio'])
    area_cost.set(areastats[area_key]['cost'])
    
    fileArea = area_network_path[area_key]
    file_name_new = ImageTk.PhotoImage(file=fileArea)
    network_canvas.delete(img_network)
    img_network = network_canvas.create_image(5, 0, anchor=NW, image = file_name_new)
    network_canvas.update()
    delete_tree()
    if areasolved[area_key]:create_tree()

def showareamap(*args):
    global file_name_new
    global network_canvas
    global img_network
    global area_key
    fileArea = area_network_path[area_key]
    file_name_new = ImageTk.PhotoImage(file=fileArea)
    network_canvas.delete(img_network)
    img_network = network_canvas.create_image(5, 0, anchor=NW, image = file_name_new)
    network_canvas.update()
   
def solvestudyarea(*args):
    global p_load_info
    global areasolved
    global route_names
    global croutes
    global route_files
    global route_names_d
    global route_tree_dict
    global area_route_tree
    global routename
    global info
    global infofile
    global area_cap2
    global area_dumptime
    global wasteperhouse
    global old_waste_adjust 
    
    saveSetup()
    
    if infofile != area_key:
        info = solver.readinfo(area_problem_info[area_key])
        infofile = area_key
        old_waste_adjust[area_key] = 10
    
    travel_speed = 8 # meter per second'ActonvilleWatville'
    travel_service_ration = 4
    service_speed = float(float(travel_speed)/float(travel_service_ration)) # meter per second
    collect_times = 1 #killogram per second    
    adjustdemand = float(wasteperhouse.get())/old_waste_adjust[area_key]
    old_waste_adjust[area_key] = int(wasteperhouse.get())
    for i in info.reqArcList:
        info.demandD[i] = int(info.demandD[i]*adjustdemand)
        info.serveCostD[i] = int(info.travelCostD[i]/service_speed) + int(info.demandD[i]*collect_times)
    
    vehiclecap = int(area_cap2.get())
    maxroute = int(area_maxtrip.get())*60*60
    
    info.capacity = vehiclecap
    info.maxTrip = maxroute
    info.dumpcost = int(area_dumptime.get())*60
    
    s = solver.displaysolution(area_key, info)
    s.localsearch = local_search_flag.get()
    s.outputpath = 'Files/Solution_Routes/'
    s.outputmetaname = area_key
    s.solveandsave()
    s.genstats()
    areasolved[area_key] = True
#    print(s.solution)
    nRoutes = len(s.solution)-1
    
#    area_route_tree[area_key]['Original network'] = {}
#    area_route_tree[area_key]['Original network']['File'] = area_key + '_Full_Network.png'
#    area_route_tree[area_key]['Original network']['Key'] = 'Original network'    
#    route_files_map[area_key]['Original network'] = area_key + '_Full_Network.png'
        
    tcost_temp = s.summarystats['Total time']/(60.0*60.0)
    tcost = '%.2f'%tcost_temp
    
    deadhead_temp = s.summarystats['Total D-time']/(60.0*60.0)
    deadhead = '%.2f'%deadhead_temp
    
    timecollect_temp = tcost_temp - deadhead_temp
    timecollect = '%.2f'%timecollect_temp
    
    utility_temp = timecollect_temp/tcost_temp
    utility = '%.2f'%utility_temp
    wcollected = s.summarystats['Total load']
    
    traveltemp = float(s.summarystats['Total trav']*8/1000)
    trav = '%.0f'%traveltemp

    routecost_temp = traveltemp*int(areastats[area_key]['cost'])*4*12
    cost = '%.0f'%routecost_temp


    all_column_info = [tcost, wcollected, utility, trav, cost]
    
    area_route_tree[area_key] = {}
    area_route_tree[area_key]['All routes'] = {}
    area_route_tree[area_key]['All routes']['File'] = area_key + '_All_Routes.png'
    area_route_tree[area_key]['All routes']['Key'] = 'All routes'
    route_files_map[area_key]['All routes'] = area_key + '_All_Routes.png'
    area_route_tree[area_key]['All routes']['Columns'] = all_column_info
           
    for i in range(1, nRoutes+1):
        routename = area_key + '_Route_' + str(i) + '.png'
        nSubtrips = len(s.solution[i]['Load'])
        name = 'Route ' + str(i)
        
        tcost_temp = s.statsnp[i-1,1]/(60.0*60.0)
        tcost = '%.2f'%tcost_temp
        
        deadhead_temp = s.statsnp[i-1,4]/(60.0*60.0)
        deadhead = '%.2f'%deadhead_temp
        
        timecollect_temp = tcost_temp - deadhead_temp
        timecollect = '%.2f'%timecollect_temp
        
        utility_temp = timecollect_temp/tcost_temp
        utility = '%.2f'%utility_temp
        wcollected = s.statsnp[i-1,7]
        
        traveltemp = float(s.statsnp[i-1,-1]*8/1000)
        trav = '%.0f'%traveltemp

        routecost_temp = traveltemp*int(areastats[area_key]['cost'])*4*12
        routecost = '%.0f'%routecost_temp

        all_column_info = [tcost, wcollected, utility, trav, routecost]        
        
        area_route_tree[area_key][i] = {}
        area_route_tree[area_key][i]['Columns'] = all_column_info
        area_route_tree[area_key][i]['File'] = routename
        area_route_tree[area_key][i]['Key'] = name
        area_route_tree[area_key][i]['Subroutes'] = {}
        route_files_map[area_key][name] = routename
        
        for j in range(1,nSubtrips+1):
            routename = area_key + '_Route_' + str(i) + '_Trip_' + str(j) + '.png'
            name = 'Subroute ' + str(i) + '.' + str(j)

            tcost_temp = s.solution[i]['Subtrip cost'][j-1]/(60.0*60.0)
            tcost = '%.2f'%tcost_temp
            
            deadhead_temp = s.solution[i]['Dead head'][j-1]/(60.0*60.0)
            deadhead = '%.2f'%deadhead_temp
            
            timecollect_temp = tcost_temp - deadhead_temp
            timecollect = '%.2f'%timecollect_temp
            
            utility_temp = timecollect_temp/tcost_temp
            utility = '%.2f'%utility_temp
            wcollected = s.solution[i]['Load'][j-1]

            traveltemp = float(s.solution[i]['Dist'][j-1]*8/1000)
            trav = '%.0f'%traveltemp
            
            routecost_temp = traveltemp*int(areastats[area_key]['cost'])*4*12
            routecost = '%.0f'%routecost_temp
            
            all_column_info = [tcost, wcollected, utility, trav, routecost]   
            
            area_route_tree[area_key][i]['Subroutes'][j] = {}
            area_route_tree[area_key][i]['Subroutes'][j]['Columns'] = all_column_info
            area_route_tree[area_key][i]['Subroutes'][j]['File'] = routename
            area_route_tree[area_key][i]['Subroutes'][j]['Key'] = name
            route_files_map[area_key][name] = routename
    
    create_tree()

def saveSetup():
    global area_key
    global areastats
    global area_waste
    global area_cap2
    global area_cost
    
    areastats[area_key]['waste'] = area_waste.get()
    areastats[area_key]['nedges'] = area_arcs.get()
    areastats[area_key]['nreqges'] = area_reqarcs.get()
    areastats[area_key]['wasteperhouse']= wasteperhouse.get()
    
    areastats[area_key]['nroues'] = area_vehicles.get()
    areastats[area_key]['cap'] = area_cap.get()
    areastats[area_key]['maxroute'] = area_maxtrip.get()
    areastats[area_key]['dumptime'] = area_dumptime.get()
    areastats[area_key]['compactratio'] =  area_compac.get()
    areastats[area_key]['cost'] = area_cost.get()
    
    newareawaste = int(areastats[area_key]['households'])*int(areastats[area_key]['wasteperhouse'])
    areastats[area_key]['waste'] = newareawaste
    area_waste.set(newareawaste)

    neweffectivecap = int(areastats[area_key]['cap'])*int(areastats[area_key]['compactratio'])*134
    areastats[area_key]['effectivecap'] = area_cap2.get()
    area_cap2.set(neweffectivecap)

def create_tree():
    global area_route_tree
    global tree_exists
    global current_list_area
    global current_area_key
    global current_area_route_tree
    
    delete_tree()
    tree_exists = True
    
    current_list_area = area_key
   
    rnameP = area_route_tree[area_key]['All routes']['Key']
    tree.insert('', 'end', rnameP, text=rnameP, values=area_route_tree[area_key]['All routes']['Columns'])

    current_area_route_tree = []
    current_area_route_tree.append('All routes')
    
    for i in range(1,len(area_route_tree[area_key])):
        rnameP = area_route_tree[area_key][i]['Key']
        current_area_route_tree.append(rnameP)
        tree.insert('', 'end', rnameP, text=rnameP, values=area_route_tree[area_key][i]['Columns'])
        for j in range(1,len(area_route_tree[area_key][i]['Subroutes'])+1):
            rnameC = area_route_tree[area_key][i]['Subroutes'][j]['Key']
            tree.insert(rnameP, 'end', rnameC, text=rnameC, values=area_route_tree[area_key][i]['Subroutes'][j]['Columns'])

    global file_name_new
    global network_canvas
    global img_network

    fileArea = 'Files/Solution_Routes/' + route_files_map[area_key]['All routes']
    file_name_new = ImageTk.PhotoImage(file=fileArea)
    network_canvas.delete(img_network)
    img_network = network_canvas.create_image(5, 0, anchor=NW, image = file_name_new)
    network_canvas.update()

def delete_tree():
    global area_route_tree
    global tree_exists
    global current_list_area
    global current_area_route_tree
    
    if tree_exists:
        for i in current_area_route_tree:
            tree.delete(i)
    current_area_route_tree = []
    tree_exists = False

def showRoute(*args):
    global file_name_new
    global network_canvas
    global img_network
    global area_key

    fileArea = 'Files/Solution_Routes/' + route_files_map[area_key][tree.selection()[0]]
    file_name_new = ImageTk.PhotoImage(file=fileArea)
    network_canvas.delete(img_network)
    img_network = network_canvas.create_image(5, 0, anchor=NW, image = file_name_new)
    network_canvas.update()


  
# Content
content = ttk.Frame(root, padding=(5))

# Frames
frame_info = ttk.Frame(content, width=100, height=100,padding=(5))
frame_network = ttk.Frame(content, width=100, height=100,padding=(5))

# Study area
lf_area = ttk.Labelframe(frame_info, text='Study area', padding=(5))
area_one = ttk.Radiobutton(lf_area, text="Actonville", command=showareastats, variable=area,  value='Actonville')
area_two = ttk.Radiobutton(lf_area, text="Watville", command=showareastats, variable=area, value='Watville')
area_three = ttk.Radiobutton(lf_area, text="Actonville & Watville", command=showareastats, variable=area, value='ActonvilleWatville')

# Study area information labels
lf_areainfo = ttk.Labelframe(frame_info, text='Study area information', padding=(5))

area_roadsegmentslbl = ttk.Label(lf_areainfo,text="Number of road segments")
area_roadsegmentsvallbl = ttk.Label(lf_areainfo,textvariable=area_arcs)

area_reqroadsegmentslbl = ttk.Label(lf_areainfo,text="Number of segments with waste")
area_reqroadsegmentsvallbl = ttk.Label(lf_areainfo,textvariable=area_reqarcs)

area_perhouselbl = ttk.Label(lf_areainfo,text="Waste per household")
area_perhousevarlbl = ttk.Entry(lf_areainfo,width=5,textvariable=wasteperhouse,justify='right')
area_prehousevarunit = ttk.Label(lf_areainfo,text="kg")

area_wastelbl = ttk.Label(lf_areainfo,text="Amount of waste in area")
area_wastevallbl = ttk.Label(lf_areainfo,textvariable=area_waste)
area_wasteunitlbl = ttk.Label(lf_areainfo,text="kg")

# Fleet setup information labels
lf_fleet = ttk.Labelframe(frame_info, text='Fleet setup', padding=(5))

fleet_nrouteslbl = ttk.Label(lf_fleet,text="Number of collection days")
fleet_nroutesval = ttk.Entry(lf_fleet,width=5,textvariable=area_vehicles,justify='right')

fleet_daylengthlbl = ttk.Label(lf_fleet,text="Work day length")
fleet_daylengthval = ttk.Entry(lf_fleet,width=5,textvariable=area_maxtrip,justify='right')
fleet_daylengthunitlbl = ttk.Label(lf_fleet,text="hours")

fleet_dumptimelbl = ttk.Label(lf_fleet,text="Dump time")
fleet_dumptimeval = ttk.Entry(lf_fleet,width=5,textvariable=area_dumptime,justify='right')
fleet_dumptimeunitlbl = ttk.Label(lf_fleet,text="minutes")

fleet_caplbl = ttk.Label(lf_fleet,text="Vehicle capacity")
fleet_capval = ttk.Entry(lf_fleet,width=5,textvariable=area_cap,justify='right')
fleet_capunitlbl = ttk.Label(lf_fleet,text="cubic meters")

fleet_compactlbl = ttk.Label(lf_fleet,text="Compact ratio (1:x)")
fleet_compacval = ttk.Entry(lf_fleet,width=5,textvariable=area_compac,justify='right')

fleet_caplbl2 = ttk.Label(lf_fleet,text="Effective vehicle capacity")
fleet_capval2 = ttk.Label(lf_fleet,textvariable=area_cap2)
fleet_capval2unitlbl = ttk.Label(lf_fleet,text="kg")

fleet_costlbl = ttk.Label(lf_fleet,text="Vehicle cost")
fleet_costval = ttk.Entry(lf_fleet,width=5,textvariable=area_cost,justify='right')
fleet_capvalunitlbl = ttk.Label(lf_fleet,text="R/km")

# Solver settings
lf_solver = ttk.Labelframe(frame_info, text="Solver settings", padding=(5))
solver_check = ttk.Checkbutton(lf_solver, text="Activate Local Search", variable=local_search_flag)

f_buttons = ttk.Labelframe(frame_info, text="Actions", padding=5)
fleet_capture_values_btn = ttk.Button(f_buttons, text="Save setup", command=saveSetup, default='active')
genroutes = ttk.Button(f_buttons, text="Generate collection routes", command=solvestudyarea, default='active')

# Network map
file_name = ImageTk.PhotoImage(file='Files/Network_Maps/ActonvilleWatville_Full_Network.jpeg')
network_canvas = Canvas(frame_network, width=800, height=315)
network_canvas.pack(expand=YES, fill=BOTH)
img_network = network_canvas.create_image(5, 0, anchor=NW, image = file_name)

# Route information
# Route tree
#lf_routeinfo = ttk.Labelframe(frame_network, text="Route statistics", padding=(5))
tree = ttk.Treeview(frame_network, columns=('total_time','load','utility','colect_time','dead_time'))

tree.column('#0', width=120, anchor='w')
tree.heading('#0', text='Route')

tree.column('total_time', width=120, anchor='e')
tree.heading('total_time', text='Total time (h)')

tree.column('load', width=120, anchor='e')
tree.heading('load', text='Waste collected (kg)')

tree.column('utility', width=120, anchor='e')
tree.heading('utility', text='Vehicle utilisation')

tree.column('colect_time', width=140, anchor='e')
tree.heading('colect_time', text='Distance travelled (km)')

tree.column('dead_time', width=140, anchor='e')
tree.heading('dead_time', text='Annual route cost (R)')

s_tree_y = ttk.Scrollbar(frame_network, orient=VERTICAL, command=tree.yview)
tree['yscrollcommand'] = s_tree_y.set

s_tree_x = ttk.Scrollbar(frame_network, orient=HORIZONTAL, command=tree.xview)
tree['xscrollcommand'] = s_tree_x.set

# Display content
content.grid(column=0, row=0, sticky=(N, S, E, W))

# Display info frame
frame_info.grid(column=0, row=0,sticky=(N,E,W))

# Display area buttons
lf_area.grid(       column=0, row=0)
area_one.grid(      column=0, row=0, sticky=(W))
area_two.grid(      column=1, row=0, sticky=(W))
area_three.grid(    column=2, row=0, sticky=(W))

# Display study area information
lf_areainfo.grid(column=0, row=1,sticky=(N,E,W))

area_roadsegmentslbl.grid(      column=0, row=0, sticky=(W))
area_roadsegmentsvallbl.grid(   column=1, row=0, sticky=(E))

area_reqroadsegmentslbl.grid(   column=0, row=1, sticky=(W))
area_reqroadsegmentsvallbl.grid(column=1, row=1, sticky=(E))

area_perhouselbl.grid(          column=0, row=2, sticky=(W))
area_perhousevarlbl.grid(       column=1, row=2, sticky=(E))
area_prehousevarunit.grid(      column=2, row=2, sticky=(W))

area_wastelbl.grid(             column=0, row=3, sticky=(W))
area_wastevallbl.grid(          column=1, row=3, sticky=(E))
area_wasteunitlbl.grid(         column=2, row=3, sticky=(W))

#area_display_area_btn.grid(     column=0, row=3, sticky=(W))

#Display fleet setup
lf_fleet.grid(column=0, row=2, sticky=(N,E,W))

fleet_nrouteslbl.grid(          column=0, row=0, sticky=(W))
fleet_nroutesval.grid(          column=1, row=0, sticky=(E))

fleet_daylengthlbl.grid(        column=0, row=2, sticky=(W))
fleet_daylengthval.grid(        column=1, row=2, sticky=(E))
fleet_daylengthunitlbl.grid(    column=2, row=2, sticky=(W))

fleet_dumptimelbl.grid(         column=0, row=3, sticky=(W))
fleet_dumptimeval.grid(         column=1, row=3, sticky=(E))
fleet_dumptimeunitlbl.grid(     column=2, row=3, sticky=(W))

fleet_caplbl.grid(              column=0, row=4, sticky=(W))
fleet_capval.grid(              column=1, row=4, sticky=(E))
fleet_capunitlbl.grid(          column=2, row=4, sticky=(W))

fleet_caplbl.grid(              column=0, row=5, sticky=(W))
fleet_capval.grid(              column=1, row=5, sticky=(E))
fleet_capunitlbl.grid(          column=2, row=5, sticky=(W))

fleet_compactlbl.grid(          column=0, row=6, sticky=(W))
fleet_compacval.grid(           column=1, row=6, sticky=(E))

fleet_caplbl2.grid(             column=0, row=7, sticky=(W))
fleet_capval2.grid(             column=1, row=7, sticky=(E))
fleet_capval2unitlbl.grid(      column=2, row=7, sticky=(W))

fleet_costlbl.grid(             column=0, row=8, sticky=(W))
fleet_costval.grid(             column=1, row=8, sticky=(E))
fleet_capvalunitlbl.grid(       column=2, row=8, sticky=(W))

#Display solver settings
lf_solver.grid(column=0, row=3, sticky=(N,E,W))
solver_check.grid(column=0, row=0, sticky=(W))

#Display buttons
f_buttons.grid(column=0, row=4, sticky=(E, W))
#fleet_capture_values_btn.grid(  column=0, row=0, sticky=(W))
genroutes.grid(column=1,row=0, sticky=(E))

#Display map
frame_network.grid(column=1, row=0, stick=N)
network_canvas.grid(column=0, row=0, sticky=(W))

#Display route statistics
#lf_routeinfo.grid(column=0, row=1, stick=(N, E, S, W))
tree.grid(column=0, row=1, sticky=(N,E,W,S))
s_tree_y.grid(column=1, row=1, sticky=(N,S))
#s_tree_x.grid(column=0, row=2, sticky=(E,W))

#Event bindings for tree
tree.bind('<<TreeviewSelect>>', showRoute)

#----------------------
area.set('Actonville')
showareastats()
root.mainloop()