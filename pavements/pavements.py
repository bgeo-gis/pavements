# -*- coding: utf-8 -*-
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *   # @UnusedWildImport
from PyQt4.QtGui import *    # @UnusedWildImport
import os.path
import sys  
from functools import partial

from dao import utils_pavements
from dao import controller
from dao.controller import DaoController


class Pavements(QObject):
   
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """          
        super(Pavements, self).__init__()
        
        # Save reference to the QGIS interface    
        self.iface = iface
        utils_pavements.setInterface(self.iface)
            
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)    
        self.plugin_name = os.path.basename(self.plugin_dir)   
        self.icon_folder = self.plugin_dir+'/icons/'        

        # initialize locale
        locale = QSettings().value('locale/userLocale')
        locale_path = os.path.join(self.plugin_dir, 'i18n', self.plugin_name+'_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
           

        # Check if config file exists    
        setting_file = os.path.join(self.plugin_dir, 'config', self.plugin_name+'.config')
        if not os.path.exists(setting_file):
            message = "Config file not found at: "+setting_file
            self.iface.messageBar().pushMessage("", message, 1, 20) 
            return  
        
        # Set plugin settings
        self.settings = QSettings(setting_file, QSettings.IniFormat)
        self.settings.setIniCodec(sys.getfilesystemencoding())  
        
        # Set QGIS settings. Stored in the registry (on Windows) or .ini file (on Unix) 
        self.qgis_settings = QSettings()
        self.qgis_settings.setIniCodec(sys.getfilesystemencoding()) 
        
        
        
        
        '''
        # Set controller to handle settings and database connection
        self.controller = DaoController(self.settings, self.plugin_name, self.iface)
        self.controller.set_qgis_settings(self.qgis_settings)
        connection_status = self.controller.set_database_connection()
        if not connection_status:
            msg = self.controller.last_error  
            self.controller.show_message(msg, 1, 100) 
            return 
            
       
        
        # Set controller to handle settings and database connection
        self.controller = DaoController(self.settings, self.plugin_name, self.iface)
        self.controller.set_qgis_settings(self.qgis_settings)
        connection_status = self.controller.set_database_connection()
        if not connection_status:
            msg = self.controller.last_error  
            self.controller.show_message(msg, 1, 100) 
            return 
        '''
        # from pavements
        # Set controller to handle settings and database
        self.controller = controller.DaoController(self.settings,)
        self.controller.setSettings(self.settings, self.plugin_name)
        #from pavements
        # Connect to Database
        self.controller.setDatabaseConnection()     
        self.dao = self.controller.getDao()  
        self.schema_name = self.controller.getSchemaName() 
            
        
         
        # Load local settings of the plugin
        self.load_plugin_settings()       
        
        self.iface.projectRead.connect(self.get_layers)   
              
        
    def initGui(self):
        """ Create the menu entries and toolbar icons inside the QGIS GUI """        
        
        self.toolbar_pavements_enabled = bool(int(self.settings.value('status/toolbar_pavements_enabled', 1)))
        if self.toolbar_pavements_enabled:
            self.toolbar_pavements_name = self.tr('toolbar_pavements_name')
            self.toolbar_pavements = self.iface.addToolBar(self.toolbar_pavements_name)
            self.toolbar_pavements.setObjectName(self.toolbar_pavements_name)              
            icon_path = self.icon_folder+'refresh.png'  
            callback_function = 'refresh_views'
            #view_name = self.schema_name+'.v_totalbudget_arc'
            self.action_refresh = self.create_action(icon_path, self.tr('refresh'), self.toolbar_pavements, None, False, callback_function, None) 
            icon_path = self.icon_folder+'define_sector.png'  
            callback_function = 'define_sector'
            self.action_define_sector = self.create_action(icon_path, self.tr('define_sector'), self.toolbar_pavements, None, False, callback_function, None) 

        
        self.get_layers()
        
        
    def load_plugin_settings(self):
        """ Load plugin settings """
        
        # Get config file
        setting_file = os.path.join(self.plugin_dir, 'config', self.plugin_name+'.config')
        self.settings = QSettings(setting_file, QSettings.IniFormat)
        self.settings.setIniCodec(sys.getfilesystemencoding())
                
        # Get plugin menu name and if own toolbar is enabled
        self.menu_name = self.tr('menu_name')        
        self.toolbar_pavements_enabled = bool(int(self.settings.value('status/toolbar_pavements_enabled', 1)))

        # Get table names    
        self.table_arc = self.settings.value('database/table_arc', 'arc')
        self.table_polygon = self.settings.value('database/table_polygon', 'polygon')
        self.table_sector = self.settings.value('database/table_sector', 'plan_psector')
        self.table_other_x_sector = self.settings.value('database/table_other_x_sector', 'plan_other_x_psector')
        
        
                    

    def tr(self, message):
        return utils_pavements.tr(self.plugin_name, message)
        
        
    def create_action(self, icon_path=None, text='', toolbar=None, menu=None, is_checkable=True, callback_function=None, view_name=None, parent=None):
        
        if parent is None:
            parent = self.iface.mainWindow()

        icon = None
        if os.path.exists(icon_path):        
            icon = QIcon(icon_path)
                
        if icon is None:
            action = QAction(text, parent) 
        else:
            action = QAction(icon, text, parent)  
                                    
        if toolbar is not None:
            toolbar.addAction(action)  
             
        if menu is not None:
            self.iface.addPluginToMenu(menu, action)
            
        try:
            action.setCheckable(is_checkable)
            callback_function = getattr(self, callback_function)
            if view_name is not None:            
                action.triggered.connect(partial(callback_function, view_name))
            else:
                action.triggered.connect(callback_function)            
        except AttributeError:
            print "Callback function not found: "+callback_function
            action.setEnabled(False)                
            
        return action   
    
    
    def get_layers(self): 
                                                                                                 
        layers = self.iface.legendInterface().layers()
        if len(layers) == 0:
            return
        # Initialize variables   
        status = True                    
        self.layer_arc = None
        self.layer_polygon = None
        self.layer_sector = None
        self.layer_other_x_sector = None
        self.schema_name = "paviments"
        table_arc = '"'+self.schema_name+'"."'+self.table_arc+'"'
        table_polygon = '"'+self.schema_name+'"."'+self.table_polygon+'"'
        table_sector = '"'+self.schema_name+'"."'+self.table_sector+'"'   
        table_other_x_sector = '"'+self.schema_name+'"."'+self.table_other_x_sector+'"'   
        self.selection_arc = []
        self.selection_polygon = [] 
        
        
        # Iterate over all layers to get the ones set in config file        
        for cur_layer in layers:
            uri = cur_layer.dataProvider().dataSourceUri().lower()   
            pos_ini = uri.find('table=')
            pos_fi = uri.find('" ')  
            uri_table = uri   
            if pos_ini <> -1 and pos_fi <> -1:
                uri_table = uri[pos_ini+6:pos_fi+1]                           
                if table_arc == uri_table:  
                    self.layer_arc = cur_layer
                if table_polygon == uri_table:
                    self.layer_polygon = cur_layer                
                if table_sector == uri_table:  
                    self.layer_sector = cur_layer                
                if table_other_x_sector == uri_table:  
                    self.layer_other_x_sector = cur_layer     

                
        
        if self.layer_arc is None:
            #utils_pavements.showWarning(self.tr("No s'ha trobat la capa: ")+table_arc)
            status = False
        if self.layer_polygon is None:
            #utils_pavements.showWarning(self.tr("No s'ha trobat la capa: ")+table_polygon)
            status = False
        if self.layer_sector is None:
            #utils_pavements.showWarning(self.tr("No s'ha trobat la capa: ")+table_sector)
            status = False
        if self.layer_other_x_sector is None:
            #utils_pavements.showWarning(self.tr("No s'ha trobat la capa: ")+table_other_x_sector)
            status = False
    
        self.action_refresh.setEnabled(status)           
        self.action_define_sector.setEnabled(status)
        if status:
            # Set signal when new feature is added in layer 'sector'
            self.layer_sector.committedFeaturesAdded.connect(self.sector_inserted)
            
        layer_source = self.controller.get_layer_source(self.layer_arc)   
        #layer_source = self.controller.get_layer_source(self.layer_version)  
        self.schema_name = layer_source['schema']
        schema_name = self.schema_name.replace('"', '')
        
        #if self.schema_name is None or not self.dao.check_schema(schema_name):
        #    self.controller.show_warning("Schema not found: "+self.schema_name)            
        #    return

        if self.layer_arc is not None:
            self.set_layer_custom_form(self.layer_arc, 'arc')
        if self.layer_polygon is not None:
            self.set_layer_custom_form(self.layer_polygon, 'pol')
        if self.layer_sector is not None:
            self.set_layer_custom_form(self.layer_sector, 'psector')


    def set_layer_custom_form(self, layer, name):
        ''' Set custom UI form and init python code of selected layer '''

        name_ui = 'form_' + name + '.ui'
        name_init = 'init_' + name + '.py'
        name_function = 'formOpen'
        file_ui = os.path.join(self.plugin_dir, 'ui', name_ui)
        file_init = os.path.join(self.plugin_dir, 'init', name_init)
        layer.editFormConfig().setUiForm(file_ui)
        layer.editFormConfig().setInitCodeSource(1)
        layer.editFormConfig().setInitFilePath(file_init)
        layer.editFormConfig().setInitFunction(name_function)


    def unload(self):
        """ Removes the plugin menu item and icon from QGIS GUI """
        if self.toolbar_pavements_enabled:    
            del self.toolbar_pavements
            
            
    # Callback functions
    
    def refresh_views(self):   
        """ Refresh materialized views """
        self.schema_name = "paviments"
        view_name = self.schema_name+'.v_totalbudget_arc'        
        sql = 'REFRESH MATERIALIZED VIEW '+view_name
        error = self.controller.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{refresh_views} - '+str(error))  
            return
        
   
        view_name = self.schema_name+'.v_totalbudget_polygon'
        sql = 'REFRESH MATERIALIZED VIEW '+view_name
        error = self.controller.execute_sql(sql)
        if error:
            utils_pavements.showWarning('{refresh_views} - '+str(error))  
            return        
        utils_pavements.showInfo(self.tr("Vistes refrescades correctament"))
        
            
    def refresh_view(self, view_name):   
        """ Refresh materialized view """ 
        sql = 'REFRESH MATERIALIZED VIEW '+str(view_name)
        error = self.dao.execute_sql(sql)
        if error:
            utils_pavements.showInfo("Vista actualitzada correctament: "+view_name)
            
            
    def define_sector(self, view_name):   
        """ Save into memory id's of selected features of the layers: arc, polygon """
        
        # Reset previous selection
        self.selection_arc = []
        self.selection_polygon = []

        # Get selected features: 'arc' and 'polygon'
        features = self.layer_arc.selectedFeatures()
        
        for f in features:
            attr = f.attributes()    
            self.selection_arc.append(attr[0])
        self.selection_arc.sort()
        
        features = self.layer_polygon.selectedFeatures()
        for f in features:
            attr = f.attributes()    
            self.selection_polygon.append(attr[0])
        self.selection_polygon.sort()
         
        # Start editing layer 'sector'
        self.iface.legendInterface().setCurrentLayer(self.layer_sector)
        self.layer_sector.startEditing()
        # Show message to help user
        utils_pavements.showInfo(self.tr("Si us plau, dibuixi el sector. Pot utilitzar el plugin CADDigitize"))
        

    def sector_inserted(self):
        """ Function called when a new sector has been inserted """      
          
        # Get last id
        sql = "SELECT MAX(CAST(psector_id as int)) FROM "+self.schema_name+".plan_psector"
        row = self.dao.get_row(sql)
        if not row:
            error = self.dao.get_last_error()
            utils_pavements.showWarning(str(error))
            return
        
        # Iterate over selected arcs and insert into table 'plan_arc_x_psector'
        psector_id = row[0]
        total_arc = 0
        if self.selection_arc is not None:
            sql = ""
            sql_common = "INSERT INTO "+self.schema_name+".plan_arc_x_psector (arc_id, psector_id) VALUES ("
            for elem in self.selection_arc:
                sql+= sql_common+"'"+str(elem)+"', '"+str(psector_id)+"');\n"
                total_arc+=1
            if sql <> "":
                error = self.dao.execute_sql(sql)
                if error:     
                    utils_pavements.showWarning('{sector_inserted.arc} - '+str(error))  
                    return   
        
        # Iterate over selected polygons and insert into table 'plan_polygon_x_psector'
        total_pol = 0        
        if self.selection_polygon is not None:        
            sql = ""
            sql_common = "INSERT INTO "+self.schema_name+".plan_polygon_x_psector (pol_id, psector_id) VALUES ("
            for elem in self.selection_polygon:
                sql+= sql_common+"'"+str(elem)+"', '"+str(psector_id)+"');\n"
                total_pol+=1
            if sql <> "":            
                error = self.dao.execute_sql(sql)
                if error:     
                    utils_pavements.showWarning('{sector_inserted.polygon} - '+str(error))  
                    return   

        # Show message to user
        #msg = "Sector creat amb codi '"+str(psector_id)+"'. Total 'arcs': "+str(total_arc)+". Total 'polygons': "+str(total_pol)
        #utils_pavements.showInfo(msg)
        
        # TODO: Preguntar Vols esborrar els registres previs del selector de sectors? Nota: Això no esborra sectors antics
#         if answer == YES:
#             sql = "DELETE FROM "+self.schema_name+".plan_psector_selection"
#             error = self.dao.execute_sql(sql)
#             if error is not None:     
#                 utils_pavements.showWarning('{sector_inserted} - '+str(error))  
#                 return           
        
        # Add this sector to table 'plan_psector_selection'
        sql = "INSERT INTO "+self.schema_name+".plan_psector_selection (id) VALUES ('"+str(psector_id)+"')"
        error = self.dao.execute_sql(sql)
        if error is not None:     
            utils_pavements.showWarning('{sector_inserted} - '+str(error))  
            return                  
        
        # Open attribute table of layer 'plan_other_x_psector'
        #self.iface.legendInterface().setCurrentLayer(self.layer_other_x_sector)    
        #self.iface.actionOpenTable().trigger()        
                
