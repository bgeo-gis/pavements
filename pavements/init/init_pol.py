# -*- coding: utf-8 -*-
from PyQt4.QtCore import *   #@UnusedWildImport
from PyQt4.QtGui import *    #@UnusedWildImport+
from qgis.utils import iface
from functools import partial
from array import *          #@UnusedWildImport
from datetime import datetime
import os.path               #@UnusedWildImport

from pavements.dao import controller
from pavements.dao import utils_pavements


def formOpen(dialog,layerid,featureid):

    global _dialog, pol_id, cbo_event, cbo_manag_type, elem_type, elem_type_text, budget_list, is_new
    global inv_index, index_collapse, index_struct, index_locat, index_superf, index_general
    global dao, mat_type_group    

    # Set global variables
    utils_pavements.setInterface(iface)      
    _dialog = dialog
    utils_pavements.setDialog(dialog)
    pol_id = _dialog.findChild(QLineEdit, "pol_id")
    cbo_event = _dialog.findChild(QComboBox, "cbo_event")
    cbo_manag_type = _dialog.findChild(QComboBox, "cbo_manag_type")
    mat_type_group = None    

    elem_type_text = _dialog.findChild(QComboBox, "elem_type").currentText()
    elem_type = 'other'
    if "ada" in elem_type_text:
        elem_type = 'roadway'
    elif elem_type_text == 'vorera':
        elem_type = 'sidewalk'
    elif elem_type_text == 'escala':
        elem_type = 'stair'

    budget_list = array('f')
    inv_index = _dialog.findChild(QLineEdit, "inv_index")
    index_collapse = _dialog.findChild(QLineEdit, "index_collapse")
    index_struct = _dialog.findChild(QLineEdit, "index_struct")
    index_locat = _dialog.findChild(QLineEdit, "index_locat")
    index_superf = _dialog.findChild(QLineEdit, "index_superf")
    index_general = _dialog.findChild(QLineEdit, "index_general")
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
    
    # Set signals to each group of radio buttons
    setSignalsGroups()

    # Wire up our own signals
    cbo_event.currentIndexChanged.connect(eventChanged)
    buttonBox.rejected.connect(_dialog.reject)
    _dialog.findChild(QLineEdit, "roadway_min_width").textChanged.connect(minWidthChanged)
    _dialog.findChild(QLineEdit, "sidewalk_min_width").textChanged.connect(minWidthChanged2)
    _dialog.findChild(QComboBox, "elem_type").currentIndexChanged.connect(elemTypeChanged)
    _dialog.findChild(QComboBox, "mat_type").currentIndexChanged.connect(matTypeChanged)
    _dialog.findChild(QComboBox, "cbo_manag_type").currentIndexChanged.connect(managTypeChanged)

    # Check if we're dealing with a new feature    
    is_new = False
    if "nextval" in pol_id.text():
        is_new = True
        manageNew()
    else:
        # Disconnect the signal that QGIS has wired up for the dialog to the button box
        buttonBox.accepted.disconnect(_dialog.accept)    
        buttonBox.accepted.connect(validate)

    # Tab 'features'
    loadFeatureData()
 
    # Tab 'status': Load data related to last event from Database
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
    logger.info('init_pol.configIni')
       
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
        pol_id.setText(str(row[0]))


def setSignalsGroups():

    setSignals("stair_accessibil")
    setSignals("sidewalk_accessibil")
    setSignals("c1_corrugat")
    setSignals("c1_crack_craz")
    setSignals("c1_crazing")
    setSignals("c1_depr_craz")
    setSignals("c1_fleshing")
    setSignals("c1_long_crack")
    setSignals("c1_pas_adhes")
    setSignals("c1_patch")
    setSignals("c1_peel_craz")
    setSignals("c1_polished")
    setSignals("c1_pothole")
    setSignals("c1_projection")
    setSignals("c1_ruttin_gen")
    setSignals("c1_rutting")
    setSignals("c1_tran_crack")
    setSignals("c3_fracture")
    setSignals("c3_homogen")
    setSignals("c3_projection")
    setSignals("c3_wear")


def minWidthChanged():
    value = _dialog.findChild(QLineEdit, "roadway_min_width").text()
    _dialog.findChild(QLineEdit, "min_width").setText(value)


def minWidthChanged2():
    value = _dialog.findChild(QLineEdit, "sidewalk_min_width").text()
    _dialog.findChild(QLineEdit, "min_width").setText(value)


# Disable and hide some controls
def disableControls():

    pol_id.setVisible(False)
    _dialog.findChild(QLineEdit, "min_width").setVisible(False)
    _dialog.findChild(QLineEdit, "c3_fracture").setVisible(False)
    _dialog.findChild(QLineEdit, "c3_homogen").setVisible(False)
    _dialog.findChild(QLineEdit, "c3_projection").setVisible(False)
    _dialog.findChild(QLineEdit, "c3_wear").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_corrugat").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_crack_craz").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_crazing").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_depr_craz").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_fleshing").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_long_crack").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_pas_adhes").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_patch").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_peel_craz").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_polished").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_pothole").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_ruttin_gen").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_rutting").setVisible(False)
    _dialog.findChild(QLineEdit, "c1_tran_crack").setVisible(False)    
    
    index_collapse.setEnabled(False)
    index_struct.setEnabled(False)
    index_locat.setEnabled(False)
    index_superf.setEnabled(False)
    index_general.setEnabled(False)
    inv_index.setEnabled(False)
    _dialog.findChild(QLineEdit, "act_budget_sum").setEnabled(False)
    _dialog.findChild(QLineEdit, "area").setEnabled(False)


# Set signal of selected group of elements
def setSignals(elem):

    group = _dialog.findChild(QButtonGroup, "group_"+elem)
    if not group:
        return
    group.buttonClicked.connect(partial(utils_pavements.elemChecked, elem))
    for i in range(7):    
        j = i+1    
        aux = _dialog.findChild(QRadioButton, elem+"_"+str(j))
        if aux:
            group.setId(aux, j)    


def elemTypeChanged():

    global elem_type, elem_type_text

    elem_type_text = _dialog.findChild(QComboBox, "elem_type").currentText()
    elem_type = 'other'
    if "ada" in elem_type_text:
        elem_type = 'roadway'
    elif elem_type_text == 'vorera':
        elem_type = 'sidewalk'
    elif elem_type_text == 'escala':
        elem_type = 'stair'
    loadFeatureData()


def matTypeChanged():

    # Check if any mat_type selected
    mat_type = _dialog.findChild(QComboBox, "mat_type").currentText()
    # Get mat_type_group from mat_type
    if "ninguna" in mat_type:
        print "Any mat_type selected"
        return

    sql = "SELECT type_matpol_id FROM paviments.cat_mat_type WHERE mattype_id = '"+mat_type+"'"
    row = dao.get_row(sql)
    if not row:
        return
       
    mat_type_group = row[0]    
    # Fill combo 'finish_pav' from 'mat_type_group'
    if "special" in mat_type_group:
        print "exit: special"
    else:
        if elem_type != 'stair':
            table_values = "value_mat_"+mat_type_group+"_finish"
            sql = "SELECT finish_id FROM paviments."+table_values+" ORDER BY finish_id"       
            rows = dao.get_rows(sql)   
            utils_pavements.fillComboBox(elem_type+"_finish_pav", rows)
            # Get selectedItem from table: 'paviments.mat_pol_"+mat_type_group'
            sql = "SELECT finish_pav FROM paviments.mat_pol_"+mat_type_group
            sql+= " WHERE pol_id = '"+pol_id.text()+"'"
            row = dao.get_row(sql)    
            utils_pavements.findText(elem_type+"_finish_pav", row[0])            


def managTypeChanged():

    value = cbo_manag_type.currentText()
    if value:
        if value == 'CI':
            _dialog.findChild(QFrame, "frame_c1").setEnabled(True)
            _dialog.findChild(QFrame, "frame_c3").setEnabled(False)
        elif value == 'CIII':
            _dialog.findChild(QFrame, "frame_c1").setEnabled(False)
            _dialog.findChild(QFrame, "frame_c3").setEnabled(True)
    else:
        _dialog.findChild(QFrame, "frame_c1").setEnabled(False)
        _dialog.findChild(QFrame, "frame_c3").setEnabled(False)


def eventChanged():

    # Check if any event selected
    event = cbo_event.currentText()
    if not event:
        utils_pavements.showWarning("Any event selected")
        return

    # Reset values
    inv_index.setText("") 
    index_collapse.setText("")
    index_struct.setText("")
    index_locat.setText("")
    index_superf.setText("")
    index_general.setText("")
    inv_team = _dialog.findChild(QLineEdit, "inv_team")
    inv_date = _dialog.findChild(QDateEdit, "inv_date")
    inv_team.setText("")
    date = datetime.strptime("2015/12/01", "%Y/%m/%d")
    inv_date.setDate(date)

    utils_pavements.resetGroup("c1_ruttin_gen")
    utils_pavements.resetGroup("c1_crazing")
    utils_pavements.resetGroup("c1_crack_craz")
    utils_pavements.resetGroup("c1_peel_craz")
    utils_pavements.resetGroup("c1_depr_craz")
    utils_pavements.resetGroup("c1_rutting")
    utils_pavements.resetGroup("c1_corrugat")
    utils_pavements.resetGroup("c1_fleshing")
    utils_pavements.resetGroup("c1_pothole")
    utils_pavements.resetGroup("c1_long_crack")
    utils_pavements.resetGroup("c1_tran_crack")
    utils_pavements.resetGroup("c1_pas_adhes")
    utils_pavements.resetGroup("c1_patch")
    utils_pavements.resetGroup("c1_polished")
    utils_pavements.resetGroup("c3_fracture")
    utils_pavements.resetGroup("c3_wear")
    utils_pavements.resetGroup("c3_projection")
    utils_pavements.resetGroup("c3_homogen")

    # Get event data from table: event_x_polygon
    sql = "SELECT date, team, manag_type, c1_ruttin_gen, c1_crazing, c1_crack_craz, c1_peel_craz, c1_depr_craz," 
    sql+= " c1_rutting, c1_corrugat, c1_fleshing, c1_pothole, c1_long_crack, c1_tran_crack, c1_pas_adhes, c1_patch, c1_polished,"
    sql+= " c3_fracture, c3_wear, c3_projection, c3_homogen"
    sql+= " FROM paviments.event_x_polygon WHERE pol_id = '"+pol_id.text()+"' and event_id = '"+event+"'"
    row = dao.get_row(sql)
    if row:
        inv_team.setText(row["team"])
        inv_date.setDate(row["date"])
        index = cbo_manag_type.findText(row["manag_type"])
        cbo_manag_type.setCurrentIndex(index);
        utils_pavements.setGroupValue("c1_ruttin_gen_"+str(row["c1_ruttin_gen"]))
        utils_pavements.setGroupValue("c1_crazing_"+str(row["c1_crazing"]))
        utils_pavements.setGroupValue("c1_crack_craz_"+str(row["c1_crack_craz"]))
        utils_pavements.setGroupValue("c1_peel_craz_"+str(row["c1_peel_craz"]))
        utils_pavements.setGroupValue("c1_depr_craz_"+str(row["c1_depr_craz"]))
        utils_pavements.setGroupValue("c1_rutting_"+str(row["c1_rutting"]))
        utils_pavements.setGroupValue("c1_corrugat_"+str(row["c1_corrugat"]))
        utils_pavements.setGroupValue("c1_fleshing_"+str(row["c1_fleshing"]))
        utils_pavements.setGroupValue("c1_pothole_"+str(row["c1_pothole"]))
        utils_pavements.setGroupValue("c1_long_crack_"+str(row["c1_long_crack"]))
        utils_pavements.setGroupValue("c1_tran_crack_"+str(row["c1_tran_crack"]))
        utils_pavements.setGroupValue("c1_pas_adhes_"+str(row["c1_pas_adhes"]))
        utils_pavements.setGroupValue("c1_patch_"+str(row["c1_patch"]))
        utils_pavements.setGroupValue("c1_polished_"+str(row["c1_polished"]))
        utils_pavements.setGroupValue("c3_fracture_"+str(row["c3_fracture"]))
        utils_pavements.setGroupValue("c3_wear_"+str(row["c3_wear"]))
        utils_pavements.setGroupValue("c3_projection_"+str(row["c3_projection"]))
        utils_pavements.setGroupValue("c3_homogen_"+str(row["c3_homogen"]))

        if row["manag_type"] == 'CI':
            manag_type = 'c1'
            _dialog.findChild(QFrame, "frame_c1").setEnabled(True)
            _dialog.findChild(QFrame, "frame_c3").setEnabled(False)
            # Get event indexes from view: v_manage_pol_c1
            sql = "SELECT area, index_collapse, index_struct, index_locat, index_superf, index_general FROM paviments.v_manage_pol_"+manag_type
            sql+= " WHERE pol_id = '"+pol_id.text()+"' and event_id = '"+event+"'"
            row2 = dao.get_row(sql)
            if row2:
                if row2["area"]:
                    aux = '%.3f' % round(row2["area"], 3)
                    _dialog.findChild(QLineEdit, "area").setText(str(aux))
                if row2["index_collapse"]:
                    aux = '%.3f' % round(row2["index_collapse"], 3)
                    index_collapse.setText(str(aux))
                else:
                    index_collapse.setText('0')
                if row2["index_struct"]:
                    aux = '%.3f' % round(row2["index_struct"], 3)
                    index_struct.setText(str(aux))
                else:
                    index_struct.setText('0')
                if row2["index_locat"]:
                    aux = '%.3f' % round(row2["index_locat"], 3)
                    index_locat.setText(str(aux))
                else:
                    index_locat.setText('0')
                if row2["index_superf"]:
                    aux = '%.3f' % round(row2["index_superf"], 3)
                    index_superf.setText(str(aux))
                else:
                    index_superf.setText('0')
                if row2["index_general"]:
                    aux = '%.3f' % round(row2["index_general"], 3)
                    index_general.setText(str(aux))
                else:
                    index_general.setText('0')
    
        elif row["manag_type"] == 'CIII':
            manag_type = 'c3'
            _dialog.findChild(QFrame, "frame_c1").setEnabled(False)
            _dialog.findChild(QFrame, "frame_c3").setEnabled(True)
            # Get event index from view: v_manage_pol_c3
            sql = "SELECT area, index FROM paviments.v_manage_pol_"+manag_type
            sql = sql + " WHERE pol_id = '"+pol_id.text()+"' and event_id = '"+event+"'"
            row2 = dao.get_row(sql)
            if row2:
                if row2["area"]:
                    aux = '%.3f' % round(row2["area"], 3)
                    _dialog.findChild(QLineEdit, "area").setText(str(aux))
                if row2["index"]:
                    aux = '%.3f' % round(row2["index"], 3)
                    inv_index.setText(str(aux))
                else:
                    inv_index.setText('0')
                    
    # Get default values from settings file
    else:
        setElem("c1_ruttin_gen")
        setElem("c1_crazing")
        setElem("c1_crack_craz")
        setElem("c1_peel_craz")
        setElem("c1_depr_craz")
        setElem("c1_rutting")
        setElem("c1_corrugat")
        setElem("c1_fleshing")
        setElem("c1_pothole")
        setElem("c1_long_crack")
        setElem("c1_tran_crack")
        setElem("c1_pas_adhes")
        setElem("c1_patch")
        setElem("c1_polished")
        setElem("c3_fracture")
        setElem("c3_wear")
        setElem("c3_projection")
        setElem("c3_homogen")


def setElem(name, default_value=5):
    value = settings.value("polygon/"+name, default_value)     
    utils_pavements.setGroupValue(name+"_"+str(value))                        


def loadFeatureData():

    if "ada" in elem_type_text or elem_type_text == 'vorera':

        # Disable controls from other types
        _dialog.findChild(QLineEdit, "stair_type").setEnabled(False)
        _dialog.findChild(QLineEdit, "width_step").setEnabled(False)
        _dialog.findChild(QLineEdit, "elev_step").setEnabled(False)
        _dialog.findChild(QLineEdit, "long_step").setEnabled(False)
        _dialog.findChild(QRadioButton, "stair_accessibil_0").setEnabled(False)
        _dialog.findChild(QRadioButton, "stair_accessibil_1").setEnabled(False)

        # Set control 'min_width'
        min_width = _dialog.findChild(QLineEdit, "min_width").text()
        aux = _dialog.findChild(QLineEdit, elem_type+"_min_width")
        aux.setText(min_width)

        matTypeChanged()

        if "ada" in elem_type_text:    

            # Disable controls from other types
            _dialog.findChild(QLineEdit, "sidewalk_min_width").setEnabled(False)
            _dialog.findChild(QRadioButton, "sidewalk_accessibil_0").setEnabled(False)
            _dialog.findChild(QRadioButton, "sidewalk_accessibil_1").setEnabled(False)

            # Fill combo 'traffic'
            sql = "SELECT traffic FROM paviments.value_traffic"
            rows = dao.get_rows(sql)               
            utils_pavements.fillComboBox("roadway_traffic", rows)

            # Get selectedItem from table 'elem_pol_roadway'
            sql = "SELECT traffic FROM paviments.elem_pol_roadway WHERE pol_id = '"+pol_id.text()+"'"
            row = dao.get_row(sql)    
            utils_pavements.findText("roadway_traffic", row[0])             

        elif elem_type_text == 'vorera':

            # Disable controls from other types
            _dialog.findChild(QLineEdit, "geom1").setEnabled(False)
            _dialog.findChild(QComboBox, "roadway_traffic").setEnabled(False)
            _dialog.findChild(QLineEdit, "roadway_min_width").setEnabled(False)

            # Load data from table 'elem_pol_sidewalk'
            sql = "SELECT accessibil FROM paviments.elem_pol_sidewalk WHERE pol_id = '"+pol_id.text()+"'"
            row = dao.get_row(sql)
            if not row:
                return
            aux = _dialog.findChild(QRadioButton, "sidewalk_accessibil_"+str(row["accessibil"]))
            if aux:
                aux.click()
            
            # Fill combo 'geom2' if any *_pavement selected
            if mat_type_group is not None and "pavement" in mat_type_group:
                sql = "SELECT geom2 FROM paviments.value_geom2"
                rows = dao.get_rows(sql)                   
                utils_pavements.fillComboBox("sidewalk_geom2", rows)
                # Get selectedItem from table 'mat_pol_"+mat_type_group'
                sql = "SELECT geom2 FROM paviments.mat_pol_"+mat_type_group+" WHERE pol_id = '"+pol_id.text()+"'"
            row = dao.get_row(sql)    
            utils_pavements.findText("sidewalk_geom2", row[0])                        

    elif elem_type_text == 'escala':

        # Disable controls from other types
        _dialog.findChild(QLineEdit, "geom1").setEnabled(False)
        _dialog.findChild(QComboBox, "roadway_traffic").setEnabled(False)
        _dialog.findChild(QLineEdit, "roadway_min_width").setEnabled(False)
        _dialog.findChild(QLineEdit, "sidewalk_min_width").setEnabled(False)
        _dialog.findChild(QRadioButton, "sidewalk_accessibil_0").setEnabled(False)
        _dialog.findChild(QRadioButton, "sidewalk_accessibil_1").setEnabled(False)

        # Load data from table 'elem_pol_stair'
        sql = "SELECT stair_type, width_step, elev_step, long_step, accessibil "
        sql = sql + "FROM paviments.elem_pol_stair WHERE pol_id = '"+pol_id.text()+"'"
        row = dao.get_row(sql)
        if not row:
            return
        _dialog.findChild(QLineEdit, "stair_type").setText(row["stair_type"])
        if row["width_step"]:     
            _dialog.findChild(QLineEdit, "width_step").setText(str(row["width_step"]))
        if row["elev_step"]:     
            _dialog.findChild(QLineEdit, "elev_step").setText(str(row["elev_step"]))
        if row["long_step"]:     
            _dialog.findChild(QLineEdit, "long_step").setText(str(row["long_step"]))
        aux = _dialog.findChild(QRadioButton, "stair_accessibil_"+str(row["accessibil"]))
        if aux:
            aux.click()


def loadStatusData():

    # Fill combo 'cbo_event'
    sql = "SELECT event_type FROM paviments.event ORDER BY id DESC"
    rows = dao.get_rows(sql)
    for row in rows:
        cbo_event.addItem(row[0])
    sql = "SELECT event_id FROM paviments.event_x_polygon WHERE pol_id = '"+pol_id.text()+"' ORDER BY date DESC"
    row = dao.get_row(sql)    
    utils_pavements.findText("cbo_event", row[0])            

    # Fill combo 'cbo_manag_type'
    sql = "SELECT id FROM paviments.type_manage"
    rows = dao.get_rows(sql)
    for row in rows:
        cbo_manag_type.addItem(row[0])

    eventChanged()


def loadOperationData():

    getOperationData('5')
    getOperationData('4')
    getOperationData('22')
    getOperationData('24')    
    getOperationData('31')
    getOperationData('41')
    getOperationData('42')
    getOperationData('44')
    getOperationData('51')
    value = 0
    for i in range(len(budget_list)):
        value = value + budget_list[i]
    value = '%.2f' % round(value, 2)
    _dialog.findChild(QLineEdit, "act_budget_sum").setText(str(value))


def getOperationData(index):

    # Disable controls
    _dialog.findChild(QLineEdit, "act_desc_"+index).setEnabled(False)
    _dialog.findChild(QLineEdit, "act_cost_"+index).setEnabled(False)
    _dialog.findChild(QLineEdit, "act_area_"+index).setEnabled(False)
    _dialog.findChild(QLineEdit, "act_percent_"+index).setEnabled(False)
    _dialog.findChild(QLineEdit, "act_budget_"+index).setEnabled(False)

    # Get data from catalog table
    sql = "SELECT descript, cost FROM paviments.manage_catalog_works WHERE id = 'w"+index+"'"
    row = dao.get_row(sql)
    if row:
        _dialog.findChild(QLineEdit, "act_desc_"+index).setText(row["descript"])
        _dialog.findChild(QLineEdit, "act_cost_"+index).setText(str(row["cost"]))

    # If view exists, get data from it
    viewname = 'v_manage_w'+str(index)
    exists = dao.check_view('paviments', viewname)
    if exists:      
        sql = "SELECT area, percent, budget FROM paviments."+viewname+" WHERE pol_id = '"+pol_id.text()+"'"
        row2 = dao.get_row(sql)
        if row2:
            _dialog.findChild(QLineEdit, "act_area_"+index).setText(str(row2["area"]))
            _dialog.findChild(QLineEdit, "act_percent_"+index).setText(str(row2["percent"]))
            _dialog.findChild(QLineEdit, "act_budget_"+index).setText(str(row2["budget"]))
            budget_list.append(row2["budget"])


# Save data from Tab 'feature' into Database
def saveFeature():

    if "ada" in elem_type_text:
        saveRoadway()

    elif elem_type_text == 'vorera':
        saveSidewalk()

    elif elem_type_text == 'escala':
        saveStair()


def saveRoadway():
        
        # Save data into table: 'elem_pol_roadway'
        elem_min_width = _dialog.findChild(QLineEdit, elem_type+"_min_width").text()
        _dialog.findChild(QLineEdit, "min_width").setText(elem_min_width)
        traffic = _dialog.findChild(QComboBox, "roadway_traffic").currentText()
        if traffic:
            traffic_value = "'"+traffic+"'"
        else:
            traffic_value = "null"
        traffic_text = "traffic = "+traffic_value
        
        # Set SQL
        sql = "UPDATE paviments.elem_pol_roadway"
        sql+= " SET "+traffic_text
        sql+= " WHERE pol_id = '"+pol_id.text()+"'"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveRoadway.update} - '+str(error))
            return False
           
        # If any row has been updated, then we need to perform an INSERT    
        rowcount = dao.get_rowcount()
        if (rowcount==0 and traffic_value!="null"):
            sql = "INSERT INTO paviments.elem_pol_roadway(pol_id, traffic) VALUES ('"+pol_id.text()+"', "+traffic_value+")"            
            error = dao.execute_sql(sql)
            if error:
                utils_pavements.showWarning('{saveRoadway.insert} - '+str(error))  
                return False                              

        # Save data into table: 'paviments.mat_pol_"+mat_type_group'
        if mat_type_group is None or "ninguna" in mat_type_group:        
            return True
        
        finish = _dialog.findChild(QComboBox, "roadway_finish_pav").currentText()
        if "(ninguna" in finish or not finish:
            finish_value = "null"
        else:
            finish_value = "'"+finish+"'"
        finish_text = "finish_pav = "+finish_value  
 
        # Set SQL
        sql = "UPDATE paviments.mat_pol_"+mat_type_group
        sql+= " SET "+finish_text
        sql+= " WHERE pol_id = '"+pol_id.text()+"'"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveRoadway.update_2} - '+str(error))  
            return False      
    
        # If any row has been updated, then we need to perform an INSERT    
        rowcount = dao.get_rowcount()
        if (rowcount == 0 and finish_value!="null"):
            sql = "INSERT INTO paviments.mat_pol_"+mat_type_group+"(pol_id, finish_pav) VALUES ('"+pol_id.text()+"', "+finish_value+")"
            error = dao.execute_sql(sql)
            if error:
                utils_pavements.showWarning('{saveRoadway.insert_2} - '+str(error))  
                return False

        return True
    

def saveSidewalk():

        # Save data into table: 'elem_pol_sidewalk'
        elem_min_width = _dialog.findChild(QLineEdit, elem_type+"_min_width").text()
        _dialog.findChild(QLineEdit, "min_width").setText(elem_min_width)
        aux_0 = _dialog.findChild(QRadioButton, elem_type+"_accessibil_0")
        aux_1 = _dialog.findChild(QRadioButton, elem_type+"_accessibil_1")
        if not (aux_0 and aux_1):
            return
        if aux_0.isChecked():
            accessibil_value = '0'
        elif aux_1.isChecked():
            accessibil_value = '1'
        else:
            accessibil_value = "null"
        accessibil_text = "accessibil = "+accessibil_value
        
        # Set SQL
        sql = "UPDATE paviments.elem_pol_sidewalk"
        sql+= " SET "+accessibil_text
        sql+= " WHERE pol_id = '"+pol_id.text()+"'"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveSidewalk} - '+str(error))  
            return      
    
        # If any row has been updated, then we need to perform an INSERT    
        rowcount = dao.get_rowcount()
        if (rowcount == 0 and accessibil_value != 'null'):
            sql = "INSERT INTO paviments.elem_pol_sidewalk(pol_id, accessibil) VALUES ('"+pol_id.text()+"', "+accessibil_value+")"
            error = dao.execute_sql(sql)
            if error:
                utils_pavements.showWarning('{saveSidewalk} - '+str(error))  
                return                        

        # Save data into table: 'paviments.mat_pol_"+mat_type_group'
        if "ninguna" in mat_type_group: 
            return
        finish = _dialog.findChild(QComboBox, elem_type+"_finish_pav").currentText()
        if "(ninguna" in finish or not finish:
            finish_value = "null"
        else:
            finish_value = "'"+finish+"'"
        finish_text = "finish_pav = "+finish_value
        if "pavement" in mat_type_group:
            has_geom2 = True
            geom2 = _dialog.findChild(QComboBox, elem_type+"_geom2").currentText()
            if "(ninguna" in geom2 or not geom2:
                geom2_value = "null"
            else:
                geom2_value = "'"+geom2+"'"
            geom2_text = "geom2 = "+geom2_value
        else:
            has_geom2 = False
        
        # Check if table exists (to avoid SQL errors)
        exists = dao.check_table('paviments', 'mat_pol_'+mat_type_group)    
        if not exists:
            print "Not exists: mat_pol_"+mat_type_group
            return
        
        # Set SQL
        sql = "UPDATE paviments.mat_pol_"+mat_type_group
        sql+= " SET "+finish_text
        if has_geom2:
            sql+= ", "+geom2_text
        sql+= " WHERE pol_id = '"+pol_id.text()+"'"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveSidewalk} - '+str(error))  
            return      
        
        # If any row has been updated, then we need to perform an INSERT    
        rowcount = dao.get_rowcount()
        if rowcount == 0:
            sql = "INSERT INTO paviments.mat_pol_"+mat_type_group+"(pol_id, finish_pav"
            if has_geom2:
                sql+= ", geom2"
            sql+= ") VALUES ('"+pol_id.text()+"', "+finish_value
            if has_geom2:
                sql+= ", "+geom2_value
            sql+= ")"
            error = dao.execute_sql(sql)
            if error:
                utils_pavements.showWarning('{saveSidewalk} - '+str(error))  


def saveStair():

        aux_0 = _dialog.findChild(QRadioButton, elem_type+"_accessibil_0")
        aux_1 = _dialog.findChild(QRadioButton, elem_type+"_accessibil_1")
        if not (aux_0 and aux_1):
            return
        if aux_0.isChecked():
            accessibil_value = '0'
        elif aux_1.isChecked():
            accessibil_value = '1'
        else:
            accessibil_value = "null"
        accessibil_text = "accessibil = "+accessibil_value

        # Create SQL
        sql = "UPDATE paviments.elem_pol_stair"
        sql+= " SET "+utils_pavements.getStringValue("stair_type")+", "+utils_pavements.getValue("width_step")+", "+utils_pavements.getValue("elev_step")+", "+utils_pavements.getValue("long_step")+", "+accessibil_text
        sql+= " WHERE pol_id = '"+pol_id.text()+"'"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveStair} - '+str(error))  
            return      
    
        # If any row has been updated, then we need to perform an INSERT        
        rowcount = dao.get_rowcount()
        if rowcount == 0:
            sql = "INSERT INTO paviments.elem_pol_stair VALUES('"+pol_id.text()+"', "+utils_pavements.getStringValue2("stair_type")+", "+utils_pavements.getValue2("width_step")
            sql+= ", "+utils_pavements.getValue2("elev_step")+", "+utils_pavements.getValue2("long_step")+", "+accessibil_value+")"
            error = dao.execute_sql(sql)
            if error:
                utils_pavements.showWarning('{saveStair} - '+str(error))              
            

def validateStatus():
    
    # Get selected event
    event = _dialog.findChild(QComboBox, "cbo_event").currentText()
    if not event:
        utils_pavements.showWarning("Any event selected")
        return False
    return True

    
# Save data from Tab 'status' into Database
def saveStatus():

    event = _dialog.findChild(QComboBox,"cbo_event").currentText()
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

    # Set SQL
    sql = "UPDATE paviments.event_x_polygon"
    sql+= " SET "+date_text+", "+team_text+", "+manag_text+", "+utils_pavements.getValue("c1_ruttin_gen")+", "+utils_pavements.getValue("c1_crazing")+", "+utils_pavements.getValue("c1_crack_craz")+", "+utils_pavements.getValue("c1_peel_craz")
    sql+= ", "+utils_pavements.getValue("c1_depr_craz")+", "+utils_pavements.getValue("c1_rutting")+", "+utils_pavements.getValue("c1_corrugat")+", "+utils_pavements.getValue("c1_fleshing")+", "+utils_pavements.getValue("c1_pothole")
    sql+= ", "+utils_pavements.getValue("c1_long_crack")+", "+utils_pavements.getValue("c1_tran_crack")+", "+utils_pavements.getValue("c1_pas_adhes")+", "+utils_pavements.getValue("c1_patch")+", "+utils_pavements.getValue("c1_polished")
    sql+= ", "+utils_pavements.getValue("c3_fracture")+", "+utils_pavements.getValue("c3_wear")+", "+utils_pavements.getValue("c3_projection")+", "+utils_pavements.getValue("c3_homogen")
    sql+= " WHERE pol_id = '"+pol_id.text()+"' and event_id = '"+event+"'"
    error = dao.execute_sql(sql)
    if error is not None:
        utils_pavements.showWarning('{saveStatus.update} - '+str(error))  
        return False 
    
    # If any row has been updated, then we need to perform an INSERT      
    rowcount = dao.get_rowcount()
    if rowcount == 0:
        sql = "INSERT INTO paviments.event_x_polygon VALUES(nextval('paviments.event_x_polygon_seq'), '"+event+"', '"+pol_id.text()+"', "+manag_value
        sql+= ", "+utils_pavements.getValue2("c1_ruttin_gen")+", "+utils_pavements.getValue2("c1_crazing")+", "+utils_pavements.getValue2("c1_crack_craz")+", "+utils_pavements.getValue2("c1_peel_craz")
        sql+= ", "+utils_pavements.getValue2("c1_depr_craz")+", "+utils_pavements.getValue2("c1_rutting")+", "+utils_pavements.getValue2("c1_corrugat")+", "+utils_pavements.getValue2("c1_fleshing")+", "+utils_pavements.getValue2("c1_pothole")
        sql+= ", "+utils_pavements.getValue2("c1_long_crack")+", "+utils_pavements.getValue2("c1_tran_crack")+", "+utils_pavements.getValue2("c1_pas_adhes")+", "+utils_pavements.getValue2("c1_patch")+", "+utils_pavements.getValue2("c1_polished")
        #sql+= ", null, null, null, null, null, null, null, null, null" 
        sql+= ", "+utils_pavements.getValue2("c3_fracture")+", "+utils_pavements.getValue2("c3_wear")+", "+utils_pavements.getValue2("c3_projection")+", "+utils_pavements.getValue2("c3_homogen")
        sql+= ", '"+date_value+"', "+team_value+", null)"
        error = dao.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{saveStatus.insert} - '+str(error))  
            return False             


def validate():

    if not is_new:
        if validateStatus():
            status = saveStatus()
            if status:
                saveFeature()
                # Return the form as accepted to QGIS.
                _dialog.accept()
    else:
        _dialog.accept()
        
        