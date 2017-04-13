# -*- coding: utf-8 -*-
from PyQt4.QtCore import *  #@UnusedWildImport
from PyQt4.QtGui import *   #@UnusedWildImport
from qgis.utils import iface
from functools import partial
from array import *         #@UnusedWildImport
from datetime import datetime
import os.path


import sys  

from pavements.dao import controller
#from dao import utils_pavements
from pavements.dao import utils_pavements
#from dao.controller import DaoController
#import utils_pavements



def formOpen(dialog, layerid, featureid):

    global _dialog, arc_id, inv_index, cbo_event, cbo_manag_type, budget_list, is_new, dao

    # Set global variables
    utils_pavements.setInterface(iface) 
    _dialog = dialog
    utils_pavements.setDialog(dialog)
    arc_id = _dialog.findChild(QLineEdit, "arc_id")
    inv_index = _dialog.findChild(QLineEdit, "inv_index")
    cbo_event = _dialog.findChild(QComboBox, "cbo_event")
    cbo_manag_type = _dialog.findChild(QComboBox, "cbo_manag_type")
    budget_list = array('f')
    buttonBox = _dialog.findChild(QDialogButtonBox, "ok_cancel")

    # Initial configuration
    if not configIni():
        return
    
    
    

    # Set controller to handle settings and database
    dao_controller = controller.DaoController(settings)
    dao_controller.setSettings(settings, plugin_name)
    
    # Connect to Database
    dao_controller.setDatabaseConnection()     
    dao = dao_controller.getDao()  
    
    # Check if we're dealing with a new feature	
    is_new = False
    if "nextval" in arc_id.text():
        is_new = True
        manageNew()
    else:
        # Disconnect the signal that QGIS has wired up for the dialog to the button box
        buttonBox.accepted.disconnect(_dialog.accept)	
        buttonBox.accepted.connect(validate)
        
    # Set signals to each group of radio buttons
    setSignals("fracture")
    setSignals("wear")
    setSignals("alignment")
    setSignals("sag")
    setSignals("grouting")

    # Wire up our own signals
    cbo_event.currentIndexChanged.connect(eventChanged)
    buttonBox.rejected.connect(_dialog.reject)

    # Tab 'features and status': Load data related to last event from Database
    loadStatusData()

    # Tab 'operation': 
    loadOperationData()

    # Disable and set invisible some controls
    disableControls()


def configIni():
    
    global logger, settings, plugin_name
    
    # Set daily log file
    plugin_name = 'pavements'  
    utils_pavements.set_logging('log', plugin_name)
    logger = utils_pavements.logging.getLogger(plugin_name)
    logger.info('init.configIni')
       
    # Get plugin directory
    user_folder = os.path.expanduser("~") 
    plugin_dir = os.path.join(user_folder, '.qgis2/python/plugins/'+plugin_name)     
    
    # Get config file
    setting_file = os.path.join(plugin_dir, 'config', plugin_name.lower()+'.config')
    if not os.path.isfile(setting_file):
        msg = "Config file not found at: "+setting_file
        logger.warning(msg)
        utils_pavements.showWarning(msg)
        return False
     
    # Load local settings of the plugin                   
    settings = QSettings(setting_file, QSettings.IniFormat)
    return True
            
        
def manageNew():

    sql = "SELECT nextval('paviments.objectid_seq'::regclass)"
    row = dao.get_row(sql)
    if row:
        arc_id.setText(str(row[0]))


# Disable and set invisible some controls
def disableControls():

    arc_id.setVisible(False)
    _dialog.findChild(QLineEdit, "fracture").setVisible(False)
    _dialog.findChild(QLineEdit, "wear").setVisible(False)
    _dialog.findChild(QLineEdit, "alignment").setVisible(False)
    _dialog.findChild(QLineEdit, "sag").setVisible(False)
    _dialog.findChild(QLineEdit, "grouting").setVisible(False)
    inv_index.setEnabled(False)

    _dialog.findChild(QLineEdit, "act_budget_sum").setEnabled(False)
    _dialog.findChild(QLineEdit, "length").setEnabled(False)
    for i in range(2):
        index = str(i+1)
        _dialog.findChild(QLineEdit, "act_desc_"+index).setEnabled(False)
        _dialog.findChild(QLineEdit, "act_cost_"+index).setEnabled(False)
        _dialog.findChild(QLineEdit, "act_length_"+index).setEnabled(False)
        _dialog.findChild(QLineEdit, "act_percent_"+index).setEnabled(False)
        _dialog.findChild(QLineEdit, "act_budget_"+index).setEnabled(False)


# Set signal all radio buttons of selected button group
def setSignals(elem):
    group = _dialog.findChild(QButtonGroup, "group_"+elem)
    group.buttonClicked.connect(partial(utils_pavements.elemChecked, elem))
    group.setId(_dialog.findChild(QRadioButton, elem+"_1"), 1)
    group.setId(_dialog.findChild(QRadioButton, elem+"_3"), 3)
    group.setId(_dialog.findChild(QRadioButton, elem+"_5"), 5)
   

def eventChanged():

    # Get data from eventx_arc table
    event = cbo_event.currentText()
    if not event:
        utils_pavements.showWarning("Any event selected")
        return

    # Reset values
    inv_index.setText("")
    inv_team = _dialog.findChild(QLineEdit, "inv_team")
    inv_date = _dialog.findChild(QDateEdit, "inv_date")
    inv_team.setText("")
    date = datetime.strptime("2015/12/01", "%Y/%m/%d")
    inv_date.setDate(date)
    utils_pavements.resetGroup("fracture")
    utils_pavements.resetGroup("wear")
    utils_pavements.resetGroup("alignment")
    utils_pavements.resetGroup("sag")
    utils_pavements.resetGroup("grouting")

    # Get event index from view: v_manage_arc_c3
    length = _dialog.findChild(QLineEdit, "length")
    sql = "SELECT index, length FROM paviments.v_manage_arc_c3 WHERE arc_id = '"+arc_id.text()+"' and event_id = '"+event+"'"
    row = dao.get_row(sql)
    if row:
        if row["index"]:
            aux = '%.3f' % round(row["index"], 3)
            inv_index.setText(str(aux))
        else:
            inv_index.setText('0')
        if row["length"]:
            aux = '%.3f' % round(row["length"], 3)
            length.setText(str(aux))
    else:
        inv_index.setText('0')

    # Get event data from table: event_x_arc
    sql = "SELECT date, team, manag_type, fracture, wear, alignment, sag, grouting"
    sql = sql + " FROM paviments.event_x_arc WHERE arc_id = '"+arc_id.text()+"' and event_id = '"+event+"'"
    row = dao.get_row(sql)
    if row:
        inv_team.setText(row["team"])
        inv_date.setDate(row["date"])
        index = cbo_manag_type.findText(row["manag_type"])
        cbo_manag_type.setCurrentIndex(index);
        utils_pavements.setGroupValue("fracture_"+str(row["fracture"]))
        utils_pavements.setGroupValue("wear_"+str(row["wear"]))
        utils_pavements.setGroupValue("alignment_"+str(row["alignment"]))
        utils_pavements.setGroupValue("sag_"+str(row["sag"]))
        utils_pavements.setGroupValue("grouting_"+str(row["grouting"]))
    # Get default values from settings file
    else:
        setElem("fracture")
        setElem("wear")
        setElem("alignment")
        setElem("sag")
        setElem("grouting")


def setElem(name, default_value=1):
    value = settings.value("arc/"+name, default_value)     
    utils_pavements.setGroupValue(name+"_"+str(value))    
    

def loadStatusData():

    # Fill combo 'cbo_event'
    sql = "SELECT event_type FROM paviments.event ORDER BY id DESC"
    rows = dao.get_rows(sql)
    for row in rows:
        cbo_event.addItem(row[0])
    sql = "SELECT event_id FROM paviments.event_x_arc WHERE arc_id = '"+arc_id.text()+"' ORDER BY date DESC"
    row = dao.get_row(sql)    
    utils_pavements.findText("cbo_event", row[0])

    # Fill combo 'cbo_manag_type'
    sql = "SELECT id FROM paviments.type_manage"
    rows = dao.get_rows(sql)
    for row in rows:
        cbo_manag_type.addItem(row[0])

    eventChanged()


def loadOperationData():

    getOperationData('1')
    getOperationData('2')
    value = 0
    for i in range(len(budget_list)):
        value = value + budget_list[i]
    value = '%.2f' % round(value, 2)
    _dialog.findChild(QLineEdit, "act_budget_sum").setText(str(value))


def getOperationData(index):

    # Get data from catalog table
    sql = "SELECT descript, cost FROM paviments.manage_catalog_works WHERE id = 'w"+index+"'"
    row = dao.get_row(sql)
    if row:
        _dialog.findChild(QLineEdit, "act_desc_"+index).setText(row["descript"])
        _dialog.findChild(QLineEdit, "act_cost_"+index).setText(str(row["cost"]))

    # Get data from view
    sql = "SELECT length, percent, budget FROM paviments.v_manage_w"+index+" WHERE arc_id = '"+arc_id.text()+"'"
    row = dao.get_row(sql)
    if row:
        _dialog.findChild(QLineEdit, "act_length_"+index).setText(str(row["length"]))
        _dialog.findChild(QLineEdit, "act_percent_"+index).setText(str(row["percent"]))
        _dialog.findChild(QLineEdit, "act_budget_"+index).setText(str(row["budget"]))
        budget_list.append(row["budget"])


def validateStatus():
    
    # Get selected event
    event = _dialog.findChild(QComboBox, "cbo_event").currentText()
    if not event:
        utils_pavements.showWarning("Any event selected")
        return False
    return True


# Save data from Tab 'status' into Database
def saveStatus():

    event = _dialog.findChild(QComboBox, "cbo_event").currentText()
    team = _dialog.findChild(QLineEdit, "inv_team")	
    if not team.text():
        team_value = "null"
    else:
        team_value = "'"+team.text()+"'"
    team_text = "team = "+team_value

    if not cbo_manag_type.currentText():
        manag_value = "null"
    else:
        manag_value = "'"+cbo_manag_type.currentText()+"'"
    manag_text = "manag_type = "+manag_value

    inv_date = _dialog.findChild(QDateEdit, "inv_date")
    date_value = inv_date.date().toString("yyyy/MM/dd")
    date_text = "date = '"+date_value+"'"

    # Create SQL
    sql = "UPDATE paviments.event_x_arc"
    sql = sql + " SET "+date_text+", "+team_text+", "+manag_text+", "+utils_pavements.getValue("fracture")+", "+utils_pavements.getValue("wear")+", "+utils_pavements.getValue("alignment")+", "+utils_pavements.getValue("sag")+", "+utils_pavements.getValue("grouting")
    sql = sql + " WHERE arc_id = '"+arc_id.text()+"' and event_id = '"+event+"'"
    error = dao.execute_sql(sql)
    if error:
        utils_pavements.showWarning('{saveStatus} - '+str(error))  
        return        
    
    # If any row has been updated, then we need to perform an INSERT      
    rowcount = dao.get_rowcount()
    if rowcount == 0:
        sql = "INSERT INTO paviments.event_x_arc VALUES(nextval('paviments.event_x_arc_seq'), '"+event+"', '"+arc_id.text()+"', "+manag_value
        sql+= ", "+utils_pavements.getValue2("fracture")+", "+utils_pavements.getValue2("wear")+", "+utils_pavements.getValue2("alignment")+", "+utils_pavements.getValue2("sag")+", "+utils_pavements.getValue2("grouting")
        sql+= ", '"+date_value+"', "+team_value+", null)"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveStatus} - '+str(error))       


def validate():
    
    if not is_new:
        if validateStatus():
            saveStatus()
            # Return the form as accepted to QGIS.
            _dialog.accept()
    else:
        _dialog.accept()

