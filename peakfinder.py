#!/usr/bin/env python
# -*- noplot -*-


from Tkinter import Tk, Button, Menu, Spinbox, W, PhotoImage, Canvas, StringVar
import tkFileDialog
import ttk
import tkFont
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg


class PeakFinder:
    def __init__(self, master):
        self.master = master
        master.title("Weiterreisswiderstand")
        self.big_font = tkFont.Font(family='Helvetica',
        size=36, weight='bold')
        self.normal_font = tkFont.Font(family='Helvetica',
        size=20, weight='normal')
        self.X = None
        self.Y = None
        self.maxima = None
        self.number_max = 0
        self.number_max_string = StringVar()
        self.max_max = 0.0
        self.max_max_string = StringVar()
        self.min_max = 0.0
        self.min_max_string = StringVar()
        self.median = 0.0
        self.median_string = StringVar()
        self.method_string = StringVar()
        self.sample_file = ''
        self.project_file = ''
        self.w = 0.0
        
        
        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialdir'] = '/home/'
        options['initialfile'] = ''
        options['parent'] = master
        options['title'] = 'Messung importieren'
   
        # This is only available on the Macintosh, and only when Navigation Services are installed.
        #options['message'] = 'message'
   
        # if you use the multiple file version of the module functions this option is set automatically.
        #options['multiple'] = 1
   
        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = '/home/'
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'This is a title'
        
        
        
        '''
        MenueLeiste
        '''
        
        ###############################################################################################
        
        self.menubar = Menu(master)
        # create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Neu", command=self.new_file, font = self.normal_font)
        self.filemenu.add_command(label="Oeffnen...", command=self.open_file, font = self.normal_font)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Messung importieren", command=self.get_filepath, font = self.normal_font)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Beenden", command=root.quit, font = self.normal_font)
        self.menubar.add_cascade(label="Datei", menu=self.filemenu, font = self.normal_font)
        
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Hilfe", command=self.greet, font = self.normal_font)
        self.helpmenu.add_command(label="Ueber", command=self.greet, font = self.normal_font)
        self.menubar.add_cascade(label="Hilfe", menu=self.helpmenu, font = self.normal_font)
        
        master.config(menu=self.menubar)
        
        ##############################################################################################
        
        
        '''
        Optionen
        '''
        self.option_label = ttk.Label(master, text = "Parameter", font = self.big_font)
        self.option_label.grid(row = 0, rowspan = 2, columnspan = 4, sticky=W)
        
        self.delta_x_label = ttk.Label(master, text = "Delta X", font = self.normal_font)
        self.delta_x_label.grid(row = 3, sticky=W)
        
        self.delta_x_spinbox = Spinbox(master, from_=10, to=500, increment = 10, font = self.normal_font, width = 3)
        self.delta_x_spinbox.grid(row = 3, column = 1)
        
        self.delta_y_label = ttk.Label(master, text = "Delta Y", font = self.normal_font)
        self.delta_y_label.grid(row = 4, column = 0, sticky=W)
        
        self.delta_y_spinbox = Spinbox(master, from_=0, to=2, increment = 0.1, font = self.normal_font, width = 3)
        self.delta_y_spinbox.grid(row = 4, column = 1)
        
        self.plot_button = Button(master, text = "Plotten", font = self.normal_font, command = self.plot, width = 10)
        self.plot_button.grid(row = 3, column = 2, columnspan = 1)
        
        self.calculate_button = Button(master, text = "Berechnen", font = self.normal_font, command = self.calculate, width = 10)
        self.calculate_button.grid(row = 4, column = 2, columnspan = 1)
        
        self.sample_thickness_label = ttk.Label(master, text = "Probendicke [mm]", font = self.normal_font)
        self.sample_thickness_label.grid(row = 5, column = 0, sticky=W)
        
        self.sample_thickness_entry = ttk.Entry(master, font = self.normal_font, width = 5)
        self.sample_thickness_entry.grid(row = 5, column = 1)

        '''
        Speichern
        '''
        self.save_label = ttk.Label(master, text = "Auswertung Speichern", font = self.big_font)
        self.save_label.grid(row = 7, rowspan = 2, columnspan = 4, sticky=W)
        
        self.sample_name_label = ttk.Label(master, text = "Probenname", font = self.normal_font)
        self.sample_name_label.grid(row = 9, sticky=W)
        
        self.sample_name_entry = ttk.Entry(master, font = self.normal_font)
        self.sample_name_entry.grid(row = 9, column = 1, columnspan = 3)
        
        self.comment_label = ttk.Label(master, text = "Kommentar", font = self.normal_font)
        self.comment_label.grid(row = 10, sticky=W)
        
        self.comment_entry = ttk.Entry(master, font = self.normal_font)
        self.comment_entry.grid(row = 10, column = 1, columnspan = 3)
        
        self.save_button = Button(master, text = "Speichern", font = self.normal_font, command = self.save, width = 10)
        self.save_button.grid(row = 12, column = 1, columnspan = 2, sticky=W)
        
        
        '''
        Analyse
        '''
        
        self.number_max_label = ttk.Label(master, text = "Anzahl Maxima:", font = self.normal_font)
        self.number_max_label.grid(row = 9, column = 6, sticky=W)
        
        self.number_max_int_label = ttk.Label(master, textvariable = self.number_max_string, font = self.normal_font)
        self.number_max_int_label.grid(row = 9, column = 7)
        
        self.max_max_label = ttk.Label(master, text = "Groesstes Maximum:", font = self.normal_font)
        self.max_max_label.grid(row = 10, column = 6, sticky=W)
        
        self.max_max_int_label = ttk.Label(master, textvariable = self.max_max_string, font = self.normal_font)
        self.max_max_int_label.grid(row = 10, column = 7)
        
        self.min_max_label = ttk.Label(master, text = "Kleinstes Maximum:", font = self.normal_font)
        self.min_max_label.grid(row = 11, column = 6, sticky=W)
        
        self.min_max_int_label = ttk.Label(master, textvariable = self.min_max_string, font = self.normal_font)
        self.min_max_int_label.grid(row = 11, column = 7)
        
        self.method_label = ttk.Label(master, text="Methode:", font = self.normal_font)
        self.method_label.grid(row = 12, column = 6, sticky=W)
        
        self.method_method_label = ttk.Label(master, textvariable = self.method_string, font = self.normal_font)
        self.method_method_label.grid(row = 12, column = 7)
        
        
        '''
        Canvas
        '''
        
        
        # Create a canvas
        self.w, self.h = 800, 500
        self.canvas = Canvas(master, width=self.w, height=self.h)
        self.canvas.grid(row = 0, column = 5, columnspan = 5, rowspan = 9)
        
        
        
        
       
        
        














    def plot(self):
        
        try:
        
            self._max, self._min = self.peakdetect(self.Y, self.X, float(self.delta_x_spinbox.get()), float(self.delta_y_spinbox.get()))
            
            self.xm = [p[0] for p in self._max]
            self.ym = [p[1] for p in self._max]
            
            self.maxima = self.ym
            self.number_max = len(self._max)
            self.number_max_string.set(str(self.number_max))
            
            self.max_max = max(self.ym)
            self.max_max_string.set(str(self.max_max))
            
            self.min_max = min(self.ym)
            self.min_max_string.set(str(self.min_max))
            
            self.fig = plt.Figure(figsize=(8, 5), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.ax.plot(self.X, self.Y)
            self.ax.plot(self.xm, self.ym, 'ro', markersize = 10)
            self.ax.axis('auto')
            self.ax.set_xlabel('Weg [cm]')
            self.ax.set_ylabel('Kraft [N]')
            self.fig_photo = self.draw_figure(self.canvas, self.fig, loc=(0, 0))
            
            if self.number_max > 1:
                self.method_string.set('Median')
            else:
                self.method_string.set('Maximum')
            
        except:
            print('Fehler')
    
    def calculate(self):
        if self.sample_thickness_entry.get() == '':
            print('Bitte Probendicke eintragen')
        else:
            if self.number_max > 1:
                self.w = self.median_calculation()
            else:
                self.w = self.one_max_calculation()
            
            
                
            
    def median_calculation(self):
        d = float(self.sample_thickness_entry.get())
        med = np.median(self.maxima)
        self.median = med
        return med/d
        
    def one_max_calculation(self):
        d = float(self.sample_thickness_entry.get())
        self.median = self.max_max
        return self.max_max/d
    
    def save(self):
        self.project_file_write = open(self.project_file, 'a')
        self.project_file_write.write('\n'+self.sample_name_entry.get()+'\t'+str(self.number_max)+'\t'+str(self.max_max)+'\t'+str(self.min_max)+'\t'+str(self.median)+'\t'+self.sample_thickness_entry.get()+'\t'+str(self.w))
        self.project_file_write.close()
    
    def new_file(self):
        self.project_file = tkFileDialog.asksaveasfilename()
        self.project_file_write = open(self.project_file, 'a')
        self.project_file_write.write('Probenname\tNMax\tMaxMax\tMinMax\tMedian\tProbendicke\Weiterreisswiderstand')
        self.project_file_write.close()
    
    def open_file(self):
        self.project_file = tkFileDialog.askopenfilename()
    
    def get_filepath(self):
        self.sample_file = tkFileDialog.askopenfilename(**self.file_opt)
        self.import_data(self.sample_file)
    
    def import_data(self, file):
        self.X, self.Y = np.loadtxt(file, usecols = (1,0), unpack = True)
        self.plot()



    def greet(self):
        print("Greetings!")
        
        
    def draw_figure(self, canvas, figure, loc=(0, 0)):
        ''' 
        Draw a matplotlib figure onto a Tk canvas
    
        loc: location of top-left corner of figure on canvas in pixels.
    
        Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
        '''
        figure_canvas_agg = FigureCanvasAgg(figure)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        photo = PhotoImage(master=canvas, width=figure_w, height=figure_h)
    
        
        # Position: convert from top-left anchor to center anchor
        canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
    
        # Unfortunatly, there's no accessor for the pointer to the native renderer
        tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    
        # Return a handle which contains a reference to the photo object
        # which must be kept live or else the picture disappears
        return photo
    
    def _datacheck_peakdetect(self, x_axis, y_axis):
        if x_axis is None:
            x_axis = range(len(y_axis))
        
        if len(y_axis) != len(x_axis):
            raise (ValueError, 
                    'Input vectors y_axis and x_axis must have same length')
        
        #needs to be a numpy array
        y_axis = np.array(y_axis)
        x_axis = np.array(x_axis)
        return x_axis, y_axis
    
    def peakdetect(self, y_axis, x_axis = None, lookahead = 300, delta=0):
        """
        Converted from/based on a MATLAB script at: 
        http://billauer.co.il/peakdet.html
        
        function for detecting local maximas and minmias in a signal.
        Discovers peaks by searching for values which are surrounded by lower
        or larger values for maximas and minimas respectively
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- (optional) A x-axis whose values correspond to the y_axis list
            and is used in the return to specify the postion of the peaks. If
            omitted an index of the y_axis is used. (default: None)
        lookahead -- (optional) distance to look ahead from a peak candidate to
            determine if it is the actual peak (default: 200) 
            '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        delta -- (optional) this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the function from picking up false peaks towards to end of
            the signal. To work well delta should be set to delta >= RMSnoise * 5.
            (default: 0)
                delta function causes a 20% decrease in speed, when omitted
                Correctly used it can double the speed of the function
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        max_peaks = []
        min_peaks = []
        dump = []   #Used to pop the first hit which almost always is false
           
        # check input data
        x_axis, y_axis = self._datacheck_peakdetect(x_axis, y_axis)
        # store data length for later use
        length = len(y_axis)
        
        
        #perform some checks
        if lookahead < 1:
            raise ValueError, "Lookahead must be '1' or above in value"
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError, "delta must be a positive number"
        
        #maxima and minima candidates are temporarily stored in
        #mx and mn respectively
        mn, mx = np.Inf, -np.Inf
        
        #Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(zip(x_axis[:-lookahead], 
                                            y_axis[:-lookahead])):
            if y > mx:
                mx = y
                mxpos = x
            if y < mn:
                mn = y
                mnpos = x
            
            ####look for max####
            if y < mx-delta and mx != np.Inf:
                #Maxima peak candidate found
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].max() < mx:
                    max_peaks.append([mxpos, mx])
                    dump.append(True)
                    #set algorithm to only find minima now
                    mx = np.Inf
                    mn = np.Inf
                    if index+lookahead >= length:
                        #end is within lookahead no more peaks can be found
                        break
                    continue
                #else:  #slows shit down this does
                #    mx = ahead
                #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
            
            ####look for min####
            if y > mn+delta and mn != -np.Inf:
                #Minima peak candidate found 
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].min() > mn:
                    min_peaks.append([mnpos, mn])
                    dump.append(False)
                    #set algorithm to only find maxima now
                    mn = -np.Inf
                    mx = -np.Inf
                    if index+lookahead >= length:
                        #end is within lookahead no more peaks can be found
                        break
                #else:  #slows shit down this does
                #    mn = ahead
                #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
        
        
        #Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump
        except IndexError:
            #no peaks were found, should the function return empty lists?
            pass
            
        return [max_peaks, min_peaks]



    




root = Tk()
my_gui = PeakFinder(root)
root.mainloop()
