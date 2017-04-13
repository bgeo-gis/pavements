# -*- coding: utf-8 -*-
from PyQt4 import uic
from PyQt4.QtCore import *    # @UnusedWildImport
from PyQt4.QtGui import *     # @UnusedWildImport
from PyQt4.QtSql import *     # @UnusedWildImport
from qgis.core import *       # @UnusedWildImport
import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'form_price_compost.ui'))


class FormPriceCompost(QDialog, FORM_CLASS):


    def __init__(self, parent=None):
        ''' Constructor '''
        super(FormPriceCompost, self).__init__(parent)
        self.setupUi(self)
        
        
    def config_ini(self, dao, utils, psector_id_selected, list_price_id):
        
        self.dao = dao
        self.utils = utils
        self.utils.setDialog(self)
        self.id.setEnabled(False)            
        self.price_id.clear()
        for elem in list_price_id:
            self.price_id.addItem(elem[0])       
                       
        self.psector_id_selected = psector_id_selected 
        self.table = "paviments.plan_other_x_psector"  
        self.filter = "psector_id = '"+self.psector_id_selected+"'" 
        self.row_cur = -1 
        self.row_total = -1   
        self.load_combos()
        self.set_signals()
        self.update_totals()  
        self.utils.setSelectedItem('psector_id', psector_id_selected)
        self.psector_id.setEnabled(False)       
        self.id.setVisible(False)       
                 
                 
    def set_signals(self):
        self.price_id.activated.connect(self.change_price_id)
        self.measurement.editingFinished.connect(self.change_measurement)                 
        self.btn_insert.clicked.connect(self.create_feature)
        self.btn_delete.clicked.connect(self.delete_feature)
        self.btn_save.clicked.connect(self.save_feature)
        self.btn_previous.clicked.connect(self.previous_feature)
        self.btn_next.clicked.connect(self.next_feature)
        #self.btn_close.clicked.connect(self.close_form)                
                
    def increase_total(self):
        total = int(self.label_total.text())
        total = total + 1
        self.label_total.setText(str(total))        
      

    def load_combos(self):
        sql = "SELECT psector_id FROM paviments.plan_psector ORDER BY psector_id"
        rows = self.dao.get_rows(sql)
        if rows:
            self.utils.fillComboBox('psector_id', rows)    
            
            
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
                    
    
    def enable_buttons(self, enable):
        self.btn_previous.setEnabled(enable)
        self.btn_next.setEnabled(enable)
        self.btn_insert.setEnabled(enable)
        self.btn_delete.setEnabled(enable)
        
    
    def previous_feature(self):
    
        self.save_feature(False)    
        self.row_cur = self.row_cur - 1;        
        if (self.row_cur <= 1):
            self.btn_previous.setEnabled(False)    
        self.btn_next.setEnabled(True)        
        self.load_feature()        
    
    
    def next_feature(self):
     
        self.save_feature(False)    
        self.row_cur = self.row_cur + 1;    
        if (self.row_cur >= self.row_total):
            self.btn_next.setEnabled(False)    
        self.btn_previous.setEnabled(True)              
        self.load_feature()   
        
        
    def create_feature(self):
    
        self.label_info.setText("Creant registre...")    
        self.reset_widgets()    
        self.enable_buttons(False)
        self.btn_save.setEnabled(True)        
    
    
    def load_feature(self):
       
        if self.row_total > 0:
            self.label_info.setText("Registre "+str(self.row_cur)+" de "+str(self.row_total))     
            sql = "SELECT id, price_id, psector_id, measurement, descript "
            sql+= " FROM paviments.plan_other_x_psector "
            sql+= " WHERE psector_id = '"+self.psector_id_selected+"' ORDER BY id"
            sql+= " LIMIT 1 OFFSET "+str(self.row_cur-1)
            row = self.dao.get_row(sql)  
            if row:    
                self.set_widgets(row)  
        else:
            self.label_info.setText("Sense registres") 
            self.reset_widgets()                             


    def set_widgets(self, row):
         
        self.id.setText(str(row['id']))
        self.utils.setSelectedItem('price_id', str(row['price_id']))
        self.utils.setText('measurement', row['measurement'])
        self.utils.setText('descript', row['descript'])
        self.change_price_id()


    def reset_widgets(self):
         
        self.id.setText('')
        self.measurement.setText('')
        self.descript.setText('')
        self.txt_price.setText('')
        self.txt_total.setText('')
        self.price_value = None
        self.measurement_value = None        
        self.change_price_id()
        

    def save_feature(self, update=False):
     
        self.enable_buttons(True)  
        id_ = self.id.text()   
        if id_:     
            # Create SQL
            sql = "UPDATE paviments.plan_other_x_psector SET "
            sql+= self.utils.getSelectedItem("price_id")+", "+self.utils.getSelectedItem("psector_id")+", "
            sql+= self.utils.getStringValue("measurement")+", "+self.utils.getStringValue("descript") 
            sql+= " WHERE id = "+self.id.text()  
            error = self.dao.execute_sql(sql) 
            if error:     
                self.utils.showWarning('{save_feature.update} - '+str(error))  
                return                
        
        else:
            sql = "INSERT INTO paviments.plan_other_x_psector (price_id, psector_id, measurement, descript) VALUES ("
            sql+= self.utils.getSelectedItem2("price_id")+", "+self.utils.getSelectedItem2("psector_id")+", "                  
            sql+= self.utils.getStringValue2("measurement")+", "+self.utils.getStringValue2("descript")+")"                
            error = self.dao.execute_sql(sql) 
            if error:     
                self.utils.showWarning('{save_feature.insert} - '+str(error))  
                return         
            self.update_totals()  
            
        
    def delete_feature(self):
    
        id_ = self.id.text()   
        if id_:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Eliminar registre")    
            msgBox.setText(u"Està segur que desitja esborrar aquest registre?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            resp = msgBox.exec_()
            if (resp == QMessageBox.Yes):
                sql = "DELETE FROM "+self.table+" WHERE id IN ("+id_+")" 
                error = self.dao.execute_sql(sql)
                if error:     
                    self.utils.showWarning('{delete_feature} - '+str(error))  
                    return     
                self.update_totals()                 


    def update_totals(self):
    
        self.row_cur = 0
        self.row_total = self.get_total()    
        if (self.row_total > 0):
            self.row_cur = 1    
            
        self.load_feature()  
        enable_previous = (self.row_cur > 1)
        enable_next = (self.row_total > self.row_cur)      
        self.btn_previous.setEnabled(enable_previous) 
        self.btn_next.setEnabled(enable_next)    
        self.btn_save.setEnabled(self.row_total > 0)
        self.btn_delete.setEnabled(self.row_total > 0)
    

    def get_total(self):
    
        row_total = -1
        sql = "SELECT COUNT(*) FROM "+self.table+" WHERE psector_id = '"+self.psector_id_selected+"'"    
        row = self.dao.get_row(sql)
        if row:     
            row_total = row[0]
        return row_total        
                    
        
    def close_form(self):
        self.close()        

