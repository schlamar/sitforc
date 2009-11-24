# coding: utf-8
'''
GUI für SITforC
'''

import gtk
import gobject
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import (FigureCanvasGTKAgg
            as FigureCanvas)
import matplotlib
import numpy as np
matplotlib.interactive(True)

from sitforc import load_csv, modellib
from sitforc.core import RegressionIdentifier, ITMIdentifier, shift_data

METHOD_REGRESSION = 0
METHOD_ITM = 1

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
        
        button = gtk.Button('CSV laden')
        button.connect('clicked', self.load_data)
        hbox.pack_start(button)
        button.show()
        
        label = gtk.Label('Daten verschieben:')
        hbox.pack_start(label, False, False, 3)
        label.show()
        
        adj = gtk.Adjustment(value=0, lower=-100, upper=100,
                             step_incr=0.1, page_incr=1.0)
        self.shift_spin = gtk.SpinButton(adjustment=adj, climb_rate=100, 
                                         digits=2)
        self.shift_spin.connect('value-changed', self.refresh)
        hbox.pack_start(self.shift_spin)
        self.shift_spin.show()
        
        reg_page = self.create_reg_page()
        itm_page = self.create_itm_page()
        
        self.method_notebook = gtk.Notebook()
        self.method_notebook.connect('switch-page', self.nb_page_switch)
        self.method_notebook.set_border_width(3)
        self.method_notebook.insert_page(reg_page, 
                                         gtk.Label('Regression'),
                                         METHOD_REGRESSION)
        self.method_notebook.insert_page(itm_page, 
                                         gtk.Label('Wendetangente'),
                                         METHOD_ITM)
        vbox.pack_start(self.method_notebook, False, False, 5)
        self.method_notebook.show()
        
        self.canvas_frame = gtk.Frame()
        vbox.pack_start(self.canvas_frame, False, False, 5)
        self.canvas_frame.show()
        
        fig = Figure()
        self.recreate_canvas(fig)
        
        self.show()
        
    def create_reg_page(self):
        reg_page = gtk.VBox()
        reg_page.show()
        
        hbox = gtk.HBox()
        reg_page.pack_start(hbox, False, False, 0)
        hbox.show()
        
        label = gtk.Label('Modell auswählen:')
        hbox.pack_start(label)
        label.show()
        
        self.model_combo = gtk.combo_box_new_text()
        self.model_combo.connect('changed', self.refresh)
        self.model_combo.append_text('')
        for modelname in sorted(model.name for model in modellib):
            self.model_combo.append_text(modelname)
        hbox.pack_start(self.model_combo)
        self.model_combo.show()
        
        button = gtk.Button('Modell anzeigen')
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
        column = gtk.TreeViewColumn('Wert', gtk.CellRendererText(), 
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
        
        label = gtk.Label('Polynomgrad:')
        table.attach(label, 0, 1, 0, 1)
        label.show()
        
        adj = gtk.Adjustment(value=11, lower=9, upper=15,
                             step_incr=2, page_incr=2)
        self.poly_degree_spin = gtk.SpinButton(adjustment=adj, digits=0)
        self.poly_degree_spin.connect('value-changed', self.refresh)
        table.attach(self.poly_degree_spin, 1, 2, 0, 1)
        self.poly_degree_spin.show()
        
        label = gtk.Label('Wendestelle:')
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
        view = gtk.TreeView(self.itm_param_lstore)
        view.set_border_width(3)
        hbox.pack_start(view, True, True, 3)
        view.show()
        
        column = gtk.TreeViewColumn('Parameter', gtk.CellRendererText(), 
                                    text=0)
        column.set_sort_column_id(0)
        view.append_column(column)
        column = gtk.TreeViewColumn('Wert', gtk.CellRendererText(), 
                                    text=1)
        column.set_sort_column_id(1)
        view.append_column(column)
        
        return itm_page
    
    def nb_page_switch(self, notebook, page, page_num):
        self.method = page_num
        self.recreate_identifier = True
        self.refresh()
        
    def change_ipoint(self, combo):
        self.ipoint_changed = True
        self.refresh()
        
    def refresh(self, *args):
        if self.data == None:
            return
        fig = Figure()
        axes = fig.add_subplot(111)
        x, y = self.data
        x, y = shift_data(x, y, self.shift_spin.get_value())
        axes.plot(x, y)
        
        if self.method == METHOD_REGRESSION: 
            modelname = self.model_combo.get_active_text()
            self.params_lstore.clear()
            try:
                model = modellib[modelname]
                self.shift_spin.set_sensitive(False)
                self.identifier = RegressionIdentifier(x, y, model)
                mf = self.identifier.model_fitter
                axes.plot(mf.x, mf.y)
                for param in sorted(mf.params.keys()):
                    value = mf.params[param]
                    self.params_lstore.append((param, '{0:.3f}'
                                                      .format(value)))
            except KeyError:
                self.shift_spin.set_sensitive(True)
            except TypeError, e:
                if str(e) == 'Improper input parameters.':
                    #TODO: msgbox
                    print 'Parameter schlecht gewählt (z.B. Verschiebung)'
                    
        elif self.method == METHOD_ITM:
            self.shift_spin.set_sensitive(True)
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
    