# -*- coding: utf-8 -*-
from PyQt4.QtCore import *  #@UnusedWildImport
from PyQt4.QtGui import *   #@UnusedWildImport
from qgis.utils import iface
from array import *         #@UnusedWildImport

from pavements.dao import controller
from pavements.dao import utils_pavements


def formOpen(dialog, layer, feature):      

    # Create class to manage Feature Form interaction  
    global other_dialog
    other_dialog = OtherDialog(iface, dialog, layer, feature)


class OtherDialog():   
    
    def __init__(self, iface, dialog, layer, feature):
        self.iface = iface
        self.dialog = dialog
        self.layer = layer
        self.feature = feature
        self.price_value = None
        self.measurement_value = None
        self.configIni()
        

    def configIni(self):
        
        # Set controller to handle settings and database
        plugin_name = 'pavements'  
        dao_controller = controller.DaoController(settings)
        dao_controller.initConfig(plugin_name)
        
        # Connect to Database
        dao_controller.setDatabaseConnection()     
        self.dao = dao_controller.getDao()
        self.schema_name = dao_controller.getSchemaName()       
        
        # Set signals
        self.price_id = self.dialog.findChild(QComboBox, "price_id")  
        self.psector_id = self.dialog.findChild(QComboBox, "psector_id")  
        self.measurement = self.dialog.findChild(QLineEdit, "measurement")   
        self.txt_price = self.dialog.findChild(QLineEdit, "txt_price")   
        self.txt_total = self.dialog.findChild(QLineEdit, "txt_total")   
        self.price_id.activated.connect(self.change_price_id)
        self.measurement.editingFinished.connect(self.change_measurement)
            
        # Initialize values
        self.txt_price.setText('')            
        self.txt_total.setText('')   
        psector = dao_controller.getSettingsParameter('status', 'psector_id')
        if psector:
            #print "init_other: "+str(psector)
            utils_pavements.setDialog(self.dialog)            
            utils_pavements.setSelectedItem("psector_id", psector)

        # Emit signal  
        self.change_price_id()
        
        
    def change_price_id(self):

        # Get price of selected 'price_id'
        price_id_selected = self.price_id.currentText()
        sql = "SELECT price FROM paviments.price_compost WHERE id = '"+price_id_selected+"'"
        row = self.dao.get_row(sql) 
        if not row:
            return
        self.price_value = row[0] 
        self.txt_price.setText(str(self.price_value)) 
        self.change_measurement()
        self.update_total()
        
        
    def change_measurement(self):
        self.measurement_value = self.measurement.text()        
        self.update_total()
                   

    def update_total(self):
        if self.measurement_value and self.price_value:
            self.measurement_value = float(self.measurement_value)
            total = float(self.price_value) * float(self.measurement_value)
            self.txt_total.setText(str(total))
        else:
            self.txt_total.setText('')             
        
        
    def save(self):
        self.dialog.accept()
        self.layer.commitChanges()    
        self.close()     
        
        
    def close(self):
        self.layer.rollBack()   
        self.dialog.parent().setVisible(False)    
    
    