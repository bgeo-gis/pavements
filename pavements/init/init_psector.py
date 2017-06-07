# -*- coding: utf-8 -*-
from PyQt4.QtCore import *  #@UnusedWildImport
from PyQt4.QtGui import *   #@UnusedWildImport
from qgis.utils import iface
from array import *         #@UnusedWildImport

from pavements.dao import controller
from pavements.dao import utils_pavements
#from ui import form_price_compost


def formOpen(dialog, layer, feature):      

    global _dialog, _iface, _layer, _feature, psector_id

    # Set global variables
    _iface = iface
    _dialog = dialog
    _layer = layer  
    _feature = feature
    utils_pavements.setInterface(iface) 
    utils_pavements.setDialog(dialog)
    #_dialog.hideButtonBox()        
        
    # Initial configuration
    if not configIni():
        return
    
    # Get Layers
    get_layers()
    
    # Set signals
    set_signals()
    
    # Check if we're dealing with a new feature  
    manage_new()


def configIni():
    
    global dao_controller, dao, schema_name, logger
    
    # Set controller to handle settings and database
    plugin_name = 'pavements'  
    #dao_controller = controller.DaoController()
    #dao_controller.initConfig(plugin_name)    


    #utils_pavements.set_logging('log', plugin_name)
    #logger = utils_pavements.logging.getLogger(plugin_name)
    #logger.info('init_pol.configIni')
       
    # Get plugin directory
    user_folder = os.path.expanduser("~") 
    plugin_dir = os.path.join(user_folder, '.qgis2/python/plugins/'+plugin_name)     
    
    # Get config file
    setting_file = os.path.join(plugin_dir, 'config', plugin_name.lower()+'.config')
    # Load local settings of the plugin                   
    settings = QSettings(setting_file, QSettings.IniFormat)
    
    # Set controller to handle settings and database
    dao_controller = controller.DaoController(settings)
    dao_controller.initConfig( plugin_name)
    
    # Connect to Database
    dao_controller.setDatabaseConnection()     
    dao = dao_controller.getDao()
    schema_name = dao_controller.getSchemaName()        
    logger = dao_controller.getLogger()   
    
    return True  
            
 
def get_layers(): 
              
    global schema_name, layer_other_x_sector
                                                           
    layers = iface.legendInterface().layers()
    if len(layers) == 0:
        return
    
    # Initialize variables                       
    layer_other_x_sector = None
    table_other_x_sector = dao_controller.getSettingsParameter('database', 'table_other_x_sector')    
    table_other_x_sector = '"'+schema_name+'"."'+table_other_x_sector+'"'   
    
    # Iterate over all layers to get the ones set in config file        
    for cur_layer in layers:     
        uri = cur_layer.dataProvider().dataSourceUri().lower()   
        pos_ini = uri.find('table=')
        pos_fi = uri.find('" ')  
        uri_table = uri   
        if pos_ini <> -1 and pos_fi <> -1:
            uri_table = uri[pos_ini+6:pos_fi+1]                                     
            if table_other_x_sector == uri_table:  
                layer_other_x_sector = cur_layer                
    
    if layer_other_x_sector is None:
        utils_pavements.showWarning("No s'ha trobat la capa: "+table_other_x_sector)
        return
        

def set_signals():
    
    global psector_id, label_total
        
    # Get widgets
    psector_id = _dialog.findChild(QLineEdit, "psector_id")
    label_total = _dialog.findChild(QLabel, "label_total")
    #btn_form_price_compost = _dialog.findChild(QPushButton, "btn_form_price_compost")
    #btn_apply = _dialog.findChild(QPushButton, "btn_apply")
    btn_accept = _dialog.findChild(QPushButton, "btn_accept")
    btn_close = _dialog.findChild(QPushButton, "btn_close")
    btn_accept.setVisible(False)
    btn_accept.setVisible(False)	
    
    # Wire up our own signals
    #btn_apply.clicked.connect(commit)
    btn_accept.clicked.connect(accept)
    btn_close.clicked.connect(close)
    #btn_form_price_compost.clicked.connect(open_form_price)   
    
         
def get_totals():
    pass
    # Get number of elements related to selected sector
    #sql = "SELECT COUNT(*) FROM paviments.plan_other_x_psector WHERE psector_id = '"+str(psector_id.text())+"'"
    #row = dao.get_row(sql)
    #if row:
    #    label_total.setText(str(row[0]))
    
    
def manage_new():

    if "nextval" in psector_id.text():
        sql = "SELECT nextval('"+schema_name+".plan_psector_seq'::regclass)"
        row = dao.get_row(sql)
        if row:
            psector_id.setText(str(row[0]))
        #btn_form_price_compost.setEnabled(False)
    else:
        # Get number of related records in table 'plan_other_x_psector'
        get_totals()        
        #btn_form_price_compost.setEnabled(True)
    
    dao_controller.setSettingsParameter('status', 'psector_id', psector_id.text())        

        
def open_form_price():
    ''' Open form to manage price_compost '''
    
    # Get list of 'price_id'
    sql = "SELECT id FROM paviments.price_compost ORDER BY id"
    rows = dao.get_rows(sql)
    if not rows:
        logger.info("No s'ha trobat cap registre a la taula 'price_compost'")  
        return
    
    # Create form
#     ui_form = ui.form_price_compost.FormPriceCompost()
#     ui_form.config_ini(dao, utils_pavements, psector_id.text(), rows)
#     
#     # Show form 
#     ui_form.exec_()
      

def commit():
    _dialog.accept()
    _layer.commitChanges()
    #btn_form_price_compost.setEnabled(True)    


def accept():
    commit()
    close()


def close():
    _dialog.parent().setVisible(False) 

