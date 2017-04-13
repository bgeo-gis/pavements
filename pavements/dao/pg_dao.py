# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras


class PgDao():
    
    
    def __init__(self):
        #self.logger = logging.getLogger('dbsync') 
        self.last_error = None
        pass

    def get_host(self):
        return self.host

    def get_last_error(self):
        return self.last_error
    '''
    def init_db(self):
        try:         
            self.conn = psycopg2.connect(self.conn_string)
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            status = True
        except psycopg2.DatabaseError, e:
            status = False
            #self.logger.warning('{pg_dao} Error %s' % e)
            #utils_pavements.showWarning('{pg_dao.init_db} - Error %s' % e)
        return status

    def set_params(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn_string = "host="+self.host+" port="+self.port+" dbname="+self.dbname+" user="+self.user+" password="+self.password
    '''
    def init_db(self):
        ''' Initializes database connection '''        
        try:
            self.conn = psycopg2.connect(self.conn_string)
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            status = True
        except psycopg2.DatabaseError, e:
            print '{pg_dao} Error %s' % e
            self.last_error = e            
            status = False
        return status


    def set_params(self, host, port, dbname, user, password):
        ''' Set database parameters '''        
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn_string = "host="+self.host+" port="+self.port
        self.conn_string+= " dbname="+self.dbname+" user="+self.user+" password="+self.password

    def set_schema_name(self, schema_name):
        self.schema_name = schema_name
        
    def get_schema_name(self):
        return self.schema_name        
        
    def get_rows(self, sql):
        self.last_error = None            
        rows = None
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception as e:
            self.last_error = e
            self.rollback()          
        finally:
            return rows                 
    
    def get_row(self, sql):
        self.last_error = None        
        row = None
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
        except psycopg2.DatabaseError, e:         
            self.last_error = e
            self.rollback()               
        finally:
            return row            

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
        
    def get_rowcount(self):
        return self.cursor.rowcount

    def commit(self):
        self.last_error = None            
        status = None        
        try:
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            status = e
            self.last_error = e            
            self.rollback()       
        finally:
            return status            
        
    def rollback(self):
        self.conn.rollback()
        self.init_db()         
        
    def check_table(self, schemaName, tableName):
        exists = True
        sql = "SELECT * FROM pg_tables WHERE schemaname = '"+schemaName+"' AND tablename = '"+tableName+"'"    
        self.cursor.execute(sql)         
        if self.cursor.rowcount == 0:      
            exists = False
        return exists       
          
    def check_view(self, schemaName, viewName):
        exists = True
        sql = "SELECT * FROM pg_views WHERE schemaname = '"+schemaName+"' AND viewname = '"+viewName+"'"    
        self.cursor.execute(sql)         
        if self.cursor.rowcount == 0:      
            exists = False
        return exists              

