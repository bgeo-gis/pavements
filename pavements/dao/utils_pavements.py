from PyQt4.QtCore import *  #@UnusedWildImport
from PyQt4.QtGui import *   #@UnusedWildImport
from qgis.gui import QgsMessageBar  #@UnresolvedImport
import logging
import os.path
import time


#
# Utility funcions
#
def tr(context, message):
    return QCoreApplication.translate(context, message)
    
    
def setInterface(p_iface):
    global iface, MSG_DURATION
    iface = p_iface
    MSG_DURATION = 10   
    
    
def setDialog(p_dialog):
    global _dialog
    _dialog = p_dialog


# Uncheck all radio buttons of selected button group
def resetGroup(elem):
    group = _dialog.findChild(QButtonGroup, "group_"+elem)
    group.setExclusive(False)
    button = group.checkedButton()
    if button:
        button.setChecked(False)
    group.setExclusive(True)
    param = _dialog.findChild(QLineEdit, elem)
    if param:
        param.setText("")


def elemChecked(widgetName):
    group = _dialog.findChild(QButtonGroup, "group_"+widgetName)
    elem = _dialog.findChild(QLineEdit, widgetName)
    if elem:
        id_ = group.checkedId()
        elem.setText(str(id_))


def setGroupValue(widgetName):
    elem = _dialog.findChild(QRadioButton, widgetName)
    if elem:
        elem.click()


def fillComboBox(widgetName, rows):
    elem = _dialog.findChild(QComboBox, widgetName)
    elem.clear()
    elem.addItem("(cap)")
    for row in rows:
        elem.addItem(row[0])


def findText(widgetName, text):
    elem = _dialog.findChild(QComboBox, widgetName)
    if elem:
        index = elem.findText(text)
        elem.setCurrentIndex(index);


def getSelectedItem(param_elem):
    elem = _dialog.findChild(QComboBox, param_elem)
    if not elem.currentText():
        elem_text = None
    else:
        elem_text = param_elem+" = '"+elem.currentText().replace("'", "''")+"'"
    return elem_text


def getSelectedItem2(param_elem):
    elem = _dialog.findChild(QComboBox, param_elem)
    if not elem.currentText():
        elem_text = "null"
    else:
        elem_text = "'"+elem.currentText().replace("'", "''")+"'"
    return elem_text


def getValue(param_elem):
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:
        if elem.text():
            elem_text = param_elem + " = "+elem.text().replace(",", ".")    
        else:
            elem_text = param_elem + " = null"
    else:
        elem_text = param_elem + " = null"
    return elem_text


def getValue2(param_elem):
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if elem.text():
            elem_text = elem.text().replace(",", ".")
        else:
            elem_text = "null"
    else:
        elem_text = "null"
    return elem_text


def getStringValue(param_elem):
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if elem.text():
            elem_text = param_elem + " = '"+elem.text()+"'"
        else:
            elem_text = param_elem + " = null"
    else:
        elem_text = param_elem + " = null"
    return elem_text


def getStringValue2(param_elem):
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:
        if elem.text():
            elem_text = "'"+elem.text()+"'"
        else:
            elem_text = "null"
    else:
        elem_text = "null"
    return elem_text


def setSelectedItem(widgetName, text):

    elem = _dialog.findChild(QComboBox, widgetName)
    if elem:
        if text is not None:
            index = elem.findText(text)
            elem.setCurrentIndex(index);
        else:
            elem.setCurrentIndex(0);
    

def isNull(param_elem):
    elem = _dialog.findChild(QLineEdit, param_elem)
    empty = True
    if elem:
        if elem.text():
            empty = False
    return empty


def setText(widgetName, text):
    
    elem = _dialog.findChild(QLineEdit, widgetName)   
    if not elem:
        return    
    value = unicode(text)
    if value == 'None':    
        elem.setText("")         
    else:
        elem.setText(value)             
        

# User interaction functions
def showInfo(text, duration = None):
    
    if duration is None:
        iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, MSG_DURATION)  
    elif duration == -1:
        iface.messageBar().pushMessage("", text, QgsMessageBar.INFO)
    else:
        iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, duration)
        
    
      
def showWarning(text, duration = None):
    
    if duration is None:
        iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, MSG_DURATION)
    elif duration == -1:
        iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING)        
    else:
        iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, duration)
        

def set_logging(log_folder, log_name):
    
    global logger 
    
    # Create logger
    if 'logger' in globals():    
#         print "Logger already defined"
        return
    
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    
    # Define filename and format
    tstamp = str(time.strftime('%Y%m%d'))
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)    
    filepath = log_folder+"/"+log_name+"_"+tstamp+".log"
    log_format = '%(asctime)s [%(levelname)s] - %(message)s\n'
    log_date = '%d/%m/%Y %H:%M:%S'
    formatter = logging.Formatter(log_format, log_date)
    
    # Create file handler
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)    
    fh.setFormatter(formatter)
    logger.addHandler(fh)    

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)        
        
