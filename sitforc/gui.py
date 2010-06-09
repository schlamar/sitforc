# coding: utf-8
'''
GUI for SITforC
'''

import gtk
import gobject
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import (FigureCanvasGTKAgg
            as FigureCanvas)
import matplotlib
matplotlib.interactive(True)

from sitforc import load_csv, modellib
from sitforc.core import RegressionIdentifier, ITMIdentifier, shift_data
from sitforc.numlib import smooth

METHOD_CORRECTION = 0
METHOD_REGRESSION = 1
METHOD_ITM = 2

class GUI(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        self.data = None
        self.identifier = None
        self.ipoint_changed = False
        self.method = METHOD_REGRESSION
        
        self.set_title('SITforC - System Identification Toolkit for '
                       'Control Theory')
        self.set_border_width(3)
        self.connect('destroy', lambda x: gtk.main_quit())
        
        vbox = gtk.VBox()
        self.add(vbox)
        vbox.show()
        
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        hbox.show()
        
        button = gtk.Button()
        box1 = gtk.HBox(False, 0)
        box1.set_border_width(2)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_SMALL_TOOLBAR)

        label = gtk.Label('Load CSV')
   
        box1.pack_start(image, False, False, 3)
        box1.pack_start(label, False, False, 3)

        image.show()
        label.show()
        box1.show()

        button.connect('clicked', self.load_data)
        button.add(box1)
        hbox.pack_start(button, True, False)
        button.show()
        
        
        corr_page = self.create_corr_page()
        reg_page = self.create_reg_page()
        itm_page = self.create_itm_page()
        
        self.method_notebook = gtk.Notebook()
        self.method_notebook.connect('switch-page', self.nb_page_switch)
        self.method_notebook.set_border_width(3)
        self.method_notebook.insert_page(corr_page, 
                                         gtk.Label('Data correction'),
                                         METHOD_CORRECTION)
        self.method_notebook.insert_page(reg_page, 
                                         gtk.Label('Regression'),
                                         METHOD_REGRESSION)
        self.method_notebook.insert_page(itm_page, 
                                         gtk.Label('Inflectional tangent'),
                                         METHOD_ITM)
        vbox.pack_start(self.method_notebook, False, False, 3)
        self.method_notebook.show()
        
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        hbox.show()
        
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_ZOOM_IN, gtk.ICON_SIZE_SMALL_TOOLBAR)
        button = gtk.Button()
        button.connect('clicked', self.zoom_in)
        button.set_image(img)
        button.set_relief(gtk.RELIEF_NONE)
        hbox.pack_end(button, False, False, 0)
        button.show()
        
        self.canvas_frame = gtk.Frame()
        vbox.pack_start(self.canvas_frame, False, False, 3)
        self.canvas_frame.show()
        
        fig = Figure()
        self.recreate_canvas(fig)
        
        self.show()
        
    def create_corr_page(self):
        page = gtk.VBox()
        page.show()
        page.set_border_width(3)
        
        hbox = gtk.HBox()
        page.pack_start(hbox, False, False, 5)
        hbox.show()
        
        label = gtk.Label('Shift data: x')
        hbox.pack_start(label, False, False, 3)
        label.show()
        
        adj = gtk.Adjustment(value=0, lower=-100, upper=100,
                             step_incr=0.1, page_incr=1.0)
        self.shift_spin = gtk.SpinButton(adjustment=adj, climb_rate=100, 
                                         digits=2)
        self.shift_spin.connect('value-changed', self.refresh)
        hbox.pack_start(self.shift_spin, False, False, 3)
        self.shift_spin.show()
        
        label = gtk.Label('y')
        hbox.pack_start(label, False, False, 3)
        label.show()
        
        adj = gtk.Adjustment(value=0, lower=-100, upper=100,
                             step_incr=0.1, page_incr=1.0)
        self.shift_spin_y = gtk.SpinButton(adjustment=adj, climb_rate=100, 
                                         digits=2)
        self.shift_spin_y.connect('value-changed', self.refresh)
        hbox.pack_start(self.shift_spin_y, False, False, 3)
        self.shift_spin_y.show()
        
        hbox = gtk.HBox()
        page.pack_start(hbox, False, False, 5)
        hbox.show()
        
        label = gtk.Label('Interpolation:')
        hbox.pack_start(label, False, False, 3)
        label.show()
        
        adj = gtk.Adjustment(value=0, lower=0, upper=200,
                             step_incr=1, page_incr=5)
        self.interpolate_spin = gtk.SpinButton(adjustment=adj, climb_rate=100, 
                                         digits=0)
        self.interpolate_spin.connect('value-changed', self.refresh)
        hbox.pack_start(self.interpolate_spin, False, False, 3)
        self.interpolate_spin.show()
        
        return page
        
    def create_reg_page(self):
        reg_page = gtk.VBox()
        reg_page.show()
        
        hbox = gtk.HBox()
        reg_page.pack_start(hbox, False, False, 0)
        hbox.show()
        
        label = gtk.Label('Choose regression model:')
        hbox.pack_start(label)
        label.show()
        
        self.model_combo = gtk.combo_box_new_text()
        self.model_combo.connect('changed', self.refresh)
        self.model_combo.append_text('')
        for modelname in sorted(model.name for model in modellib):
            self.model_combo.append_text(modelname)
        hbox.pack_start(self.model_combo)
        self.model_combo.show()
        
        button = gtk.Button('Show model')
        button.connect('clicked', self.show_model)
        hbox.pack_start(button, False, False, 3)
        button.show()
        
        hbox = gtk.HBox()
        reg_page.pack_start(hbox)
        hbox.show()
        
        self.params_lstore = gtk.ListStore(gobject.TYPE_STRING, 
                               gobject.TYPE_STRING)
        view = gtk.TreeView(self.params_lstore)
        view.set_border_width(3)
        hbox.pack_start(view, True, True, 3)
        view.show()
        
        column = gtk.TreeViewColumn('Parameter', gtk.CellRendererText(), 
                                    text=0)
        column.set_sort_column_id(0)
        view.append_column(column)
        column = gtk.TreeViewColumn('Value', gtk.CellRendererText(), 
                                    text=1)
        column.set_sort_column_id(1)
        view.append_column(column)
        
        return reg_page
    
    def create_itm_page(self):
        itm_page = gtk.VBox()
        itm_page.show()
        
        table = gtk.Table(2,2)
        table.set_border_width(5)
        table.set_row_spacings(2)
        itm_page.pack_start(table, True, False, 3)
        table.show()
        
        label = gtk.Label('Polynomial degree:')
        table.attach(label, 0, 1, 0, 1)
        label.show()
        
        adj = gtk.Adjustment(value=11, lower=9, upper=15,
                             step_incr=2, page_incr=2)
        self.poly_degree_spin = gtk.SpinButton(adjustment=adj, digits=0)
        self.poly_degree_spin.connect('value-changed', self.refresh)
        table.attach(self.poly_degree_spin, 1, 2, 0, 1)
        self.poly_degree_spin.show()
        
        label = gtk.Label('Point of inflection:')
        table.attach(label, 0, 1, 1, 2)
        label.show()
        
        self.ipoint_combo = gtk.combo_box_new_text()
        self.ipoint_combo.connect('changed', self.change_ipoint)
        table.attach(self.ipoint_combo, 1, 2, 1, 2)
        self.ipoint_combo.show()
        
        hbox = gtk.HBox()
        itm_page.pack_start(hbox)
        hbox.show()
        
        self.itm_param_lstore = gtk.ListStore(gobject.TYPE_STRING, 
                               gobject.TYPE_STRING)
        lstore = self.itm_param_lstore
        lstore.append(('Tu', ''))
        lstore.append(('Tg',''))
        lstore.append(('Tu/Tg', ''))
        lstore.append(('Tg/Tu', ''))
        
        view = gtk.TreeView(self.itm_param_lstore)
        view.set_border_width(3)
        hbox.pack_start(view, True, True, 3)
        view.show()
        
        column = gtk.TreeViewColumn('Parameter', gtk.CellRendererText(), 
                                    text=0)
        column.set_sort_column_id(0)
        view.append_column(column)
        column = gtk.TreeViewColumn('Value', gtk.CellRendererText(), 
                                    text=1)
        column.set_sort_column_id(1)
        view.append_column(column)
        
        return itm_page
    
    def zoom_in(self, button):
        if self.identifier:
            self.identifier.plot_solution()
        elif not self.data == None:
            x, y = self.process_data()
            matplotlib.pyplot.plot(x, y, label='data')
            matplotlib.pyplot.legend()
            matplotlib.pyplot.grid()
            matplotlib.pyplot.show()
    
    def nb_page_switch(self, notebook, page, page_num):
        self.method = page_num
        self.recreate_identifier = True
        self.refresh()
        
    def change_ipoint(self, combo):
        self.ipoint_changed = True
        self.refresh()
        
    def process_data(self):
        x, y = self.data
        x, y = shift_data(x, y, self.shift_spin.get_value())
        y = y - self.shift_spin_y.get_value()
        y = smooth(y, self.interpolate_spin.get_value_as_int()+2)
        return x, y
        
    def refresh(self, *args):
        if self.data == None:
            return
        fig = Figure()
        axes = fig.add_subplot(111)
        x, y = self.process_data()
        axes.plot(x, y)
        
        if self.method == METHOD_REGRESSION: 
            modelname = self.model_combo.get_active_text()
            self.params_lstore.clear()
            try:
                model = modellib[modelname]
                #self.shift_spin.set_sensitive(False)
                #self.shift_spin_y.set_sensitive(False)
                #self.interpolate_spin.set_sensitive(False)
                self.identifier = RegressionIdentifier(x, y, model)
                mf = self.identifier.model_fitter
                axes.plot(mf.x, mf.y)
                for param in sorted(mf.params.keys()):
                    value = mf.params[param]
                    self.params_lstore.append((param, '{0:.3f}'
                                                      .format(value)))
            except KeyError:
                #self.shift_spin.set_sensitive(True)
                #self.shift_spin_y.set_sensitive(True)
                #self.interpolate_spin.set_sensitive(True)
                self.identifier = None
            except TypeError as e:
                if str(e) == 'Improper input parameters.':
                    #TODO: Warning
                    print 'Parameters are badly chosen (e.g. by shifting)'
                else:
                    raise
                    
        elif self.method == METHOD_ITM:
            #self.shift_spin.set_sensitive(True)
            #self.shift_spin_y.set_sensitive(True)
            #self.interpolate_spin.set_sensitive(True)
            try:
                if self.ipoint_changed:
                    num = self.ipoint_combo.get_active()
                    if num >= 0:
                        self.identifier.calculate_inflec_point(num)
                    self.ipoint_changed = False
                else:
                    degree = self.poly_degree_spin.get_value_as_int()
                    self.identifier = ITMIdentifier(x, y, degree)
                    self.ipoint_combo.get_model().clear()
                    for x, y, xp in self.identifier.i_points:
                        text = 'x: {0:.3f}, y: {1:.3f}'.format(x, y)
                        self.ipoint_combo.append_text(text)
                ident = self.identifier
                c = ident.height
                axes.plot([ident.x[0], ident.x[-1]], [c, c], '--')
                axes.plot(ident.t_x, ident.t_y)
                
                lstore = self.itm_param_lstore
                lstore.clear()
                lstore.append(('Tu', '{0:.3f}'.format(ident.tu)))
                lstore.append(('Tg','{0:.3f}'.format(ident.tg)))
                lstore.append(('Tu/Tg', '{0:.3f}'.format(ident.tu/ident.tg)))
                lstore.append(('Tg/Tu', '{0:.3f}'.format(ident.tg/ident.tu)))
            except TypeError as e:
                if str(e) == 'expected non-empty vector for x':
                    #TODO: Warning
                    print 'Parameters are badly chosen (e.g. by shifting)'
                else:
                    raise
                
                    
        self.recreate_canvas(fig)
        self.resize(1, 1)
        
    def recreate_canvas(self, fig):
        canvas = FigureCanvas(fig)
        canvas.set_size_request(450, 200)
        if self.canvas_frame.get_child():
            self.canvas_frame.remove(self.canvas_frame.get_child())
        self.canvas_frame.add(canvas)
        canvas.show()
        
    def load_data(self, button):
        file_chooser = gtk.FileChooserDialog(title='CSV Datei laden',
                                             buttons=(gtk.STOCK_CANCEL,
                                                      gtk.RESPONSE_CANCEL,
                                                      gtk.STOCK_OPEN,
                                                      gtk.RESPONSE_OK))
        result = file_chooser.run()
        
        if result == gtk.RESPONSE_OK:
            self.data = load_csv(file_chooser.get_filename())
            self.refresh()
        file_chooser.destroy()
        
    def show_model(self, button):
        modelname = self.model_combo.get_active_text()
        try:
            model = modellib[modelname]
            model.show()
        except KeyError:
            pass
        
def start_gui():
    GUI()
    gtk.main()
    