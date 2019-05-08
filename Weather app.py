# weather from web collection and format modules
import re
import requests
import datetime
from tkinter import *  # GUI

#matplotlib import to allow it to be places in Tk GUI
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
matplotlib.use("TkAgg")


def values(url): # gets weather info from url
    print(url)
    r = requests.get(url)

    #get weather data from page souce
    min_raw = re.findall(r'<dd class="min">.*?</dd>',r.text)
    max_raw = re.findall(r'<dd class="max">.*?</dd>',r.text)
    rain_raw = re.findall(r'<dd class=\"pop\">.*?% <img',r.text)

    min_temp = []
    max_temp = []
    rain = []

    #formats data
    for i in min_raw:
        min_temp.append(int(i.replace("<dd class=\"min\">", "").replace("</dd>", "").replace(" &deg;C", "")))
    for i in max_raw:
        max_temp.append(int(i.replace("<dd class=\"max\">", "").replace("</dd>", "").replace(" &deg;C", "")))
    for i in rain_raw:
        rain.append(int(i.replace("<dd class=\"pop\">", "").replace("% <img", "")))


    today = datetime.datetime.today()
    daykey = ["Monday","Tuesday","Wednesday","Thursday ","Friday","Saturday","Sunday"]
    days = []

    for i in range(len(max_temp)+1):
        days.append(daykey[(today + datetime.timedelta(days=i)).weekday()])

    if not len(max_temp) == len(min_temp):
        max_temp = max_temp[1::]

    print(max_temp, min_temp, rain, days, url.split("/")[-2])
    return (max_temp, min_temp, rain, days, url.split("/")[-2]) # retunes fully formatted data



def plot(max, min, rain, days, place, plotF): # plots the information
    for i in plotF.winfo_children(): # remove previouse plot
        i.destroy()

    x = range(len(max))
    fig = Figure()

    ax = fig.add_subplot(211)
    ax.plot(x, max, 'r-')
    ax.plot(x, min, 'b-')

    for i,j in zip(x, max):
        ax.annotate(str(j),xy=(i,j))

    for i,j in zip(x, min):
        ax.annotate(str(j),xy=(i,j))

    # sets titles and information bars
    ax.set_title("Weather forcast for the next 6 days in %s" %place)
    ax.set_ylabel("Temperature (°C)")
    ax.set_xticklabels(days)
    ax.legend(["Max Temperature", "Min Temperature"])


    ax1 = fig.add_subplot(212)
    ax1.set_ylim(0,100)
    ax1.plot(x, rain, 'c-')

    for i,j in zip(x, rain):
        ax1.annotate("%s%%"%j,xy=(i,j))

    ax1.set_title("Chance of rain")
    ax1.set_ylabel("chance for rain (%)")
    ax1.set_xticklabels(days)



    fig.tight_layout()

    # show the plot in Tk canvas
    canvas = FigureCanvasTkAgg(fig, plotF)
    canvas.show()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)

def GetPage(url): #get towns / citys from state overview pages
    r = requests.get(url)
    places_raw = re.findall(r'<a href="/places/.*?" class=',r.text)
    placekey = {}

    for i in places_raw:
        current = "http://www.bom.gov.au/places/%s" %i.replace("<a href=\"/places/", "").replace("\" class=", "")
        placekey[current.split("/")[-2]] = current

    return placekey

def PlaceSelect(place, root, kill, plotF, locationTag): # is called when location is selected
    stateKey = {'nsw': 'New South Wales', 'vic': 'Victoria', 'qld': 'Queensland', 'wa': 'Western Australia', 'sa': 'South Australia', 'tas': 'Tasmania',
    'act': 'Australian Capital Territory', 'nt': 'Northern Territory'}

    locationTag[0].title("Australian Weather forcast - %s" %place.split("/")[-2])
    locationTag[1].config(text="%s - %s" %(stateKey[place.split("/")[-3]], place.split("/")[-2]))
    locationTag[1].pack(side=LEFT)
    plot(*values(place), plotF)
    kill.pack_forget()
    root.config(height = 24)

def LBCheck(listbox, places): # checks if listbox selected is state / teritory and disabels it being selected
    if not len(listbox.curselection()) == 0:
        if listbox.curselection()[0] in places:
            listbox.selection_clear(0, END)
            listbox.select_set(listbox.prevind)
        listbox.prevind = listbox.curselection()[0]

def GetLocation(places, root, plotF, locationTag): # generates a dropdown list (Listbox) based on available places
    locationTag[1].pack_forget()
    listbox = Listbox(root, height=14)
    listbox.pack(fill=BOTH, expand=True, side = BOTTOM)
    pos = 0
    titles = []

    for i in places:
        listbox.insert(END, i) # adds states / teritorys
        listbox.itemconfig(END, bg="#808080", fg = "#ffffff")
        titles.append(pos)
        pos += 1
        for j in places[i]:
            listbox.insert(END, j) # adds towns / cities
            listbox.itemconfig(END, bg="#ffffff", fg = "#000000")
            pos += 1

    citys = {}
    for i in places:
        citys = {**citys, **places[i]}

    listbox.select_set(1)
    listbox.prevind = 1

    listbox.bind('<<ListboxSelect>>', lambda x: LBCheck(listbox, titles))
    listbox.bind('<Double-1>', lambda x: PlaceSelect(citys[listbox.get(listbox.curselection())], root, listbox, plotF, locationTag)) # calls PlaceSelect to desplay data


def layout(): # builds base layout for GUI (Graphical user interface)
    # load places to prevent delay while in use
    places = {
    "New South Wales":GetPage("http://www.bom.gov.au/places/nsw/"),
    "Victoria":GetPage("http://www.bom.gov.au/places/vic/"),
    "Queensland ":GetPage("http://www.bom.gov.au/places/qld/"),
    "Western Australia":GetPage("http://www.bom.gov.au/places/wa/"),
    "South Australia":GetPage("http://www.bom.gov.au/places/sa/"),
    "Tasmania":GetPage("http://www.bom.gov.au/places/tas/"),
    "Australian Capital Territory":GetPage("http://www.bom.gov.au/places/act/"),
    "Northern Territory":GetPage("http://www.bom.gov.au/places/nt/")}

    # window basics - title initial size and icon
    root = Tk()
    root.title("Australian Weather forcast")
    root.geometry('1000x500')
    root.wm_iconbitmap('icon.ico')

    bar = Frame(root, width = 600, height = 24, bg = "#ffffff",highlightbackground="#808080", highlightcolor="#808080", highlightthickness=1)
    locationTag = Label(bar, text = "hello world", bg = "#ffffff", fg = "#000000")
    locationTag.pack(side=LEFT)
    bar.pack(fill=X)
    bar.bind('<Button-1>', lambda x: GetLocation(places, bar, plotF, [root, locationTag]))
    locationTag.bind('<Button-1>', lambda x: GetLocation(places, bar, plotF, [root, locationTag]))

    plotF = Frame(root, width = 600, height = 300, bg = "#ffffff")
    plotF.pack(fill=BOTH, expand = True)

    root.after(20, lambda: PlaceSelect("http://www.bom.gov.au/places/act/canberra/", bar, Text(bar), plotF, [root, locationTag]))


layout() # calls layout function wich initilaises everything
mainloop() # calls to GUI mainloop / initialises GUI
