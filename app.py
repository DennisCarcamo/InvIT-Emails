import psycopg2
import json
from psycopg2 import Error
from service.mandrill_requests import *
from configparser import ConfigParser

def executeQuery(queryString, connection):
    cursor = connection.cursor()
    cursor.execute(queryString)
    records = ''
    try:
        records = cursor.fetchall()
    except:
        print('')
    cursor.close()
    connection.close()
    return records

def executeInsertQuery2(queryString, connection):
    cursor = connection.cursor()
    cursor.execute(queryString)
    cursor.close()
    connection.commit()
    connection.close()

def extractLoans(connection):
    #getting  the Loans Pages. 
    queryString1 =  'SELECT pages.id_employee, pages.id_signature, pages.first_name, pages.last_name, pages.name, pages.status '
    queryString1 += 'FROM (SELECT sheet_sheetType.id_employee, sheet_sheetType.id_signature, sheet_sheetType.first_name, sheet_sheetType.last_name, sheet_sheetType.name, sheet_sheetType.status '
    queryString1 += 'FROM (SELECT sheet.id_employee, sheet.id_signature, sheet.first_name, sheet.last_name, sheet.email, sheet.id_type, sheetType.name, sheet.status '
    queryString1 += 'FROM (SELECT id_employee, id_signature, first_name, last_name, email, status, last, id_type '
    queryString1 += 'FROM tbl_signature_sheet) sheet '
    queryString1 += 'LEFT JOIN tbl_type as sheetType '
    queryString1 += 'ON sheet.id_type = sheetType.id_type) sheet_sheetType '
    queryString1 += 'LEFT JOIN tbl_images as images '
    queryString1 += 'ON sheet_sheetType.id_signature = images.id_signature)pages '
    queryString1 += 'WHERE pages.name = \'Loan\'; '
    results =  executeQuery(queryString1,connection)
    tempArray = []
    filtered = ""
    if results:
        for i in results:
            tempArray.append({'id_employee': i[0], 'id_signature':i[1], 'firts_name':i[2], 'last_name':i[3],'page_type':i[4], 'status': i[5]})
        queryJsonString = json.dumps(tempArray)
        jsonValues = json.loads(queryJsonString)
        filtered  =  [obj for obj in jsonValues if(obj['status'] == 1)]
    return filtered

def extractInVITEmails(connection):
    #getting the InVIT Emails
    queryString = 'SELECT id, received_by, email_exception, returned, emails_sent, id_signature '
    queryString += 'FROM tbl_invit_emails'
    results = executeQuery(queryString,connection)
    tempArray = []
    if results:
        for i in results:
            tempArray.append({'id': i[0], 'received_by':i[1], 'email_exception':i[2], 'returned':i[3],'emails_sent':i[4], 'id_signature': i[5]})
        queryJsonString = json.dumps(tempArray)
        jsonValues = json.loads(queryJsonString)
    return tempArray

def filterLoansResult(loansPagesResults, invitEmailsResults):
    #filter for just the not returned pages these will have status = 1 
    exist = False; 
    for i in loansPagesResults:
        for j in invitEmailsResults:
            if(i['id_signature'] == j['id_signature']):
                exist = True
                break
        
        if(exist == False):
            print('no existe')
            queryFix = 'INSERT INTO public.tbl_invit_emails( received_by, email_exception, returned, emails_sent, id_signature) '
            queryFix += 'VALUES (\'\', 0, 1, 3, ' + str(i['id_signature'])+ ' );'
            print(queryFix)
            try:
                connection = psycopg2.connect(connstr)
                executeInsertQuery2(queryFix,connection)
            except (Exception, psycopg2.DatabaseError) as error: 
                print ("Error", error)

def prepareEmailInfo(connection):
    queriFix =  'SELECT prod_page.id, sig.email, prod_page.id_product, prod_page.ciid, prod_page.id_signature, prod_page.product_name, prod_page.serial_number, prod_page.model,'
    queriFix += 'prod_page.received_by, prod_page.email_exception, prod_page.returned, prod_page.emails_sent, sig.updated, sig.first_name, sig.last_name '
    queriFix += 'FROM (Select prod.id, prod.id_product, prod.ciid, prod.id_signature, prod.product_name, prod.serial_number, prod.model, '
    queriFix += 'sign.received_by, sign.email_exception, sign.returned, sign.emails_sent '
    queriFix += 'FROM(SELECT received_by, email_exception, returned, emails_sent, id_signature '
    queriFix += 'FROM tbl_invit_emails) sign '
    queriFix += 'LEFT JOIN tbl_signature_x_product as prod '
    queriFix += 'ON sign.id_signature = prod.id_signature) prod_page '
    queriFix += 'LEFT JOIN tbl_signature_sheet as sig '
    queriFix += 'ON sig.id_signature = prod_page.id_signature '

    #print(queriFix)

    results = executeQuery(queriFix,connection)
    tempArray = []
    if results:
        for i in results:
            tempArray.append({'id': i[0], 'email':i[1], 'id_product':i[2], 'ciid':i[3], 'id_signature':i[4],'product_name':i[5], 'serial_number': i[6], 
            'model':i[7],'received_by':i[8], 'email_exception':i[9], 'returned':i[10], 'emails_sent':i[11], 'updated':str(i[12]),'name':i[13], 'lastname':i[14]})
        queryJsonString = json.dumps(tempArray)
        jsonValues = json.loads(queryJsonString)
    return tempArray

def addEmailCount(results):
    for item in results:
        if(item['id_page']):
            idPage = int(item['id_page'])
            #query to get the currentEmail Count
            query = ("""SELECT emails_sent 
                        FROM public.tbl_invit_emails
                        WHERE id_signature = {};""".format(idPage))
            connection = psycopg2.connect(connstr)
            result = executeQuery(query,connection)
            currentEmailCount = int(result[0][0])+1
            #print(currentEmailCount)
            connection = psycopg2.connect(connstr)
            query = ("""UPDATE public.tbl_invit_emails
                        SET emails_sent = {}
                        WHERE id_signature = {};""".format(currentEmailCount, idPage))
            executeInsertQuery2(query,connection)

if __name__ == '__main__':
    config = ConfigParser()
    config.read('C:\\Users\\dejoc\\Documents\\InvITemails\\Emails\\configurations.ini')

    admins = []
    adminEmailFrec = ''
    name = ''
    email = ''
    supervisor = []
    supervisorEmailFrec = ''
    execution = ''


    try:
        for section_name in config.sections():
        #print ('Section:', section_name)
            if str(section_name) == 'IT_ADMINISTRATORS_EMAILS':
                for name, email  in config.items(section_name):
                    admins.append({'name':name, 'email':email})
                    #print ('  %s = %s' % (name, value))
            elif (str(section_name) == 'IT_SUPERVISOR_EMAIL'):
                for name, email  in config.items(section_name):
                    supervisor.append({'name':name, 'email':email})
            elif (str(section_name) == 'EMAILS_FRECUENCY'):
                supervisorEmailFrec = config['EMAILS_FRECUENCY']['it_supervisor']
                adminEmailFrec = config['EMAILS_FRECUENCY']['it_admins']
            elif(str(section_name) == 'EXECUTION'):
                execution = config['EXECUTION']['execution']
    except:
        print('error')

    PSQL_HOST = config['dataBase']['data_base_host']
    PSQL_PORT = config['dataBase']['data_base_port']
    PSQL_USER = config['dataBase']['data_base_user']
    PSQL_PASS = config['dataBase']['data_base_password']
    PSQL_DB   = config['dataBase']['data_base_name']
    connstr = "host=%s port=%s user=%s password=%s dbname=%s" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)

    try:
        connection = psycopg2.connect(connstr)
        loansPagesResults  = extractLoans(connection)
        #print(loansPagesResults)
        connection = psycopg2.connect(connstr)
        invitEmailsResults = extractInVITEmails(connection)
        #print(invitEmailsResults)
        loansPagesResultsFiltered = filterLoansResult(loansPagesResults,invitEmailsResults);

        #getting the new InVITEmails values
        connection = psycopg2.connect(connstr)
        invitEmailsResults = extractInVITEmails(connection)

        #getting userEmails and Products
        connection = psycopg2.connect(connstr)
        resultForEmails = prepareEmailInfo(connection)

        #send emails
        results = Email.sendEmails(resultForEmails,admins,supervisor, execution, adminEmailFrec, supervisorEmailFrec)

        #set the Email Count
        addEmailCount(results)
            
    except (Exception, psycopg2.DatabaseError) as error: 
        print ("Error", error)