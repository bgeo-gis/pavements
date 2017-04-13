# -*- coding: utf-8 -*-
from PyQt4.QtCore import *   # @UnusedWildImport
from PyQt4.QtGui import *    # @UnusedWildImport
import os.path


from PyQt4.QtSql import QSqlDatabase
import subprocess

import psycopg2         #@UnusedImport
import psycopg2.extras



import utils_pavements
from pg_dao import PgDao


class DaoController():
    '''
    
    def __init__(self, settings, plugin_name, iface):
        self.settings = settings
        self.plugin_name = plugin_name
        self.iface = iface
    '''
    def __init__(self, settings):
        self.settings = settings
      
        
        
    def initConfig(self, plugin_name):

        # Set daily log file
        utils_pavements.set_logging('log', plugin_name)
        self.logger = utils_pavements.logging.getLogger(plugin_name)
        #logger.info('init_psector.configIni')
           
        # Get plugin directory
        user_folder = os.path.expanduser("~") 
        plugin_dir = os.path.join(user_folder, '.qgis2/python/plugins/'+plugin_name)     
        
        # Get config file
        setting_file = os.path.join(plugin_dir, 'config', plugin_name.lower()+'.config')
        if not os.path.isfile(setting_file):
            msg = "Config file not found at: "+setting_file
            self.logger.warning(msg)
            utils_pavements.showWarning(msg)
            return False
         
        # Load local settings of the plugin                   
        self.settings = QSettings(setting_file, QSettings.IniFormat)     

    def set_qgis_settings(self, qgis_settings):
        self.qgis_settings = qgis_settings  
    
    def getDao(self):
        return self.dao
    
    def getLogger(self):
        return self.logger
        
    def getLastError(self):
        return self.last_error
        
    def getSchemaName(self):
        return self.schema_name
    
    def getSettingsParameter(self, section, param):
        value = self.settings.value(section+"/"+param, '-1')   
        #print "get: "+str(value)
        return value     
    
    def setSettingsParameter(self, section, param, value):
        #print "set: "+str(value)
        self.settings.setValue(section+"/"+param, value)   
           
    def tr(self, message):
        return QCoreApplication.translate(self.plugin_name, message)                
    

    def setSettings(self, settings, plugin_name):
        self.settings = settings
        self.plugin_name = plugin_name
                
    
    def setDatabaseConnection(self):
        """ Look for connection data in QGIS configuration (if exists) """    
        
        # Initialize variables
        self.dao = None 
        self.last_error = None        
        self.connection_name = self.settings.value('database/connection_name', '')
        self.schema_name = self.settings.value('database/schema_name', '')
        
        qgis_settings = QSettings()     
        root_conn = "/PostgreSQL/connections/"          
        qgis_settings.beginGroup(root_conn);           
        groups = qgis_settings.childGroups();                                
        if self.connection_name in groups:      
            root = self.connection_name+"/"  
            host = qgis_settings.value(root+"host", '')
            port = qgis_settings.value(root+"port", '')            
            db = qgis_settings.value(root+"database", '')
            user = qgis_settings.value(root+"username", '')
            pwd = qgis_settings.value(root+"password", '') 
        else:
            self.last_error = self.tr('Database connection name not found. Please check configuration file')
            return False
    
        # Connect to Database 
        self.dao = PgDao()     
        self.dao.set_params(host, port, db, user, pwd)
        self.dao.set_schema_name(self.schema_name)
        status = self.dao.init_db()
       
        return status    
    
    def set_database_connection(self):
        ''' Ser database connection '''
        
        # Initialize variables
        self.dao = None 
        self.last_error = None      
        #self.connection_name = self.settings.value('db/connection_name', self.plugin_name)
        #self.schema_name = self.plugin_settings_value('schema_name')
        self.connection_name = self.settings.value('database/connection_name', '')
        self.schema_name = self.settings.value('database/schema_name', '')
        self.log_codes = {}
        
        # Look for connection data in QGIS configuration (if exists)    
        connection_settings = QSettings()       
        root_conn = "/PostgreSQL/connections/"          
        connection_settings.beginGroup(root_conn);           
        groups = connection_settings.childGroups();                                 
        if self.connection_name in groups:      
            root = self.connection_name+"/"  
            host = connection_settings.value(root+"host", '')
            port = connection_settings.value(root+"port", '')            
            db = connection_settings.value(root+"database", '')
            self.user = connection_settings.value(root+"username", '')
            pwd = connection_settings.value(root+"password", '') 
            # We need to create this connections for Table Views
            self.db = QSqlDatabase.addDatabase("QPSQL")
            self.db.setHostName(host)
            self.db.setPort(int(port))
            self.db.setDatabaseName(db)
            self.db.setUserName(self.user)
            self.db.setPassword(pwd)
            self.status = self.db.open()    
            if not self.status:
                msg = "Database connection error. Please check connection parameters"
                self.show_warning(msg)
                self.last_error = self.tr(msg)
                return False           
        else:
            msg = "Database connection name not found. Please check configuration file 'pavemanets.config'"
            self.show_warning(msg)
            self.last_error = self.tr(msg)
            return False
    
        # Connect to Database 
        self.dao = PgDao()     
        self.dao.set_params(host, port, db, self.user, pwd)
        status = self.dao.init_db()
       
        return status   
        
    def plugin_settings_value(self, key, default_value=""):
        key = self.plugin_name+"/"+key
        value = self.qgis_settings.value(key, default_value)
        return value    
        
    def plugin_settings_set_value(self, key, value):
        self.qgis_settings.setValue(self.plugin_name+"/"+key, value)   
        
        
    def show_message(self, text, message_level=1, duration=5, context_name=None):
        ''' Show message to the user.
        message_level: {INFO = 0, WARNING = 1, CRITICAL = 2, SUCCESS = 3} '''
        self.iface.messageBar().pushMessage("", self.tr(text, context_name), message_level, duration)  
        
            
    def show_info(self, text, duration=5, context_name=None):
        ''' Show message to the user.
        message_level: {INFO = 0, WARNING = 1, CRITICAL = 2, SUCCESS = 3} '''
        self.show_message(text, 0, duration, context_name)
        
        
    def show_warning(self, text, duration=5, context_name=None):
        ''' Show message to the user.
        message_level: {INFO = 0, WARNING = 1, CRITICAL = 2, SUCCESS = 3} '''
        self.show_message(text, 1, duration, context_name)
        
    '''
    def tr(self, message, context_name=None):
        if context_name is None:
            context_name = self.plugin_name
        return QCoreApplication.translate(context_name, message) 
    '''
        
        
        
    def get_layer_source(self, layer):
        ''' Get database, schema and table or view name of selected layer '''

        # Initialize variables
        layer_source = {'db': None, 'schema': None, 'table': None, 'host': None, 'username': None}
        
        # Get database name, host and port
        uri = layer.dataProvider().dataSourceUri().lower()
        pos_ini_db = uri.find('dbname=')
        pos_ini_host = uri.find(' host=')
        pos_ini_port = uri.find(' port=')
        if pos_ini_db <> -1 and pos_ini_host <> -1:
            uri_db = uri[pos_ini_db + 8:pos_ini_host - 1]
            layer_source['db'] = uri_db     
        if pos_ini_host <> -1 and pos_ini_port <> -1:
            uri_host = uri[pos_ini_host + 6:pos_ini_port]     
            layer_source['host'] = uri_host       
         
        # Get schema and table or view name     
        pos_ini_table = uri.find('table=')
        pos_end_schema = uri.rfind('.')
        pos_fi = uri.find('" ')
        if pos_ini_table <> -1 and pos_fi <> -1:
            uri_schema = uri[pos_ini_table + 6:pos_end_schema]
            uri_table = uri[pos_end_schema + 2:pos_fi]
            layer_source['schema'] = uri_schema            
            layer_source['table'] = uri_table            

        return layer_source   


    def execute_sql(self, sql, autocommit=True):
        self.last_error = None            
        status = None
        try:
            self.cursor.execute(sql) 
            if autocommit:
                self.commit()
        except psycopg2.DatabaseError, e:
            status = e
            self.last_error = e           
            self.rollback()   
        finally:
            return status