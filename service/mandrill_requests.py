import mandrill
import requests
import json
from datetime import datetime

API_KEY = 'j3VdGCRj9OsJiY5LZQlT5g'
mandrill_client =  mandrill.Mandrill(API_KEY)
mandrill_link = 'https://mandrillapp.com/api/1.0/'

class Verify():
    data = {
        "key": API_KEY
    }
    responseStruct = requests.post(mandrill_link + 'users/info.json', data = data)
    responseJSON = json.loads(responseStruct.text)

    #print(responseJSON['username']);

class Email():
    @staticmethod
    def ss(item,products):
        tempHTML = ""
        loan_date = ""
        id_page = ""
        email = item['email']
        id_page = item['id_signature']
        loan_date = item['updated']
        name = item['name']
        lastname = item['lastname']
        for element in products:
            tempHTML += "<tr>"
            tempHTML += "<td>"+element['Tag']+"</td>"
            tempHTML += "<td>"+element['Product Name']+"</td>"
            tempHTML += "<td>"+element['Serial Number']+"</td>"
            tempHTML += "</tr>"
        now = datetime.timestamp(datetime.now())
        html = """<head>
                <style>
                table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
                }

                td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
                }

                .line {
                width: 100%;
                height: 1px;
                border-bottom: 1px dashed #ddd;
                margin: 20px 0;
                }

                tr:nth-child(even) {
                background-color: #dddddd;
                }
                </style>
                </head>
                <body>
                <div class="line"></div>
                <p>Buen d&iacute;a&nbsp;"""+name+"""&nbsp;"""+lastname+""".<p>
                <p>Este es un mensaje autom&aacutetico para recordarle que la fecha de 
                entrega """+str(loan_date)+""" de su equipo en pr&eacutestamo ha vencido, 
                favor acerquese al equipo de IT para hacer la entrega del mismo o para solicitar 
                una extensi&oacuten del periodo de pr&eacutestamo.</p>
                <p>El equipo en pr&eacutestamo en su hoja """+str(id_page)+"""  es:</p>
                <table>
                <tr>
                    <th>Tag</th>
                    <th>Product Name</th>
                    <th>Serial</th>
                </tr>"""+tempHTML+"""
                </table>
                <p>De antemano, &iexcl;Muchas gracias!.</p>
                <p>Atte. Helpdesk IT.</p>
                <div class="line"></div>
                <p>&nbsp;</p>
                </body>"""    

        message = {
        'from_email': 'no.reply@laureate.net',
        'from_name': 'Helpdesk IT',
        'headers': {'Reply-To': 'no.reply@laureate.net'},
        'html': html,
        'merge_language': 'mailchimp',
        'subject': 'Return Borrowed Equipment Request',
        'tags': ['password-resets'],
        'to': [{'email': 'dennis.carcamo@laureate.net',
                'name': 'Dennis Carcamo',
                'type': 'to'}]
        }

        result = mandrill_client.messages.send(message=message, ip_pool='Main Pool')
        #print (result)
        message = """<div class="line"></div> """+ str(message)

        if result[0]['status'] == "sent":
            return {
                "result": result,
                "id_page": id_page,
                "status": 'sent',
                "message": html
            }
        else:
            return {
                "result":"error"
            }
       
    @staticmethod
    def sendAdminEmails(admin, htmlMessage):
        
        today = datetime.now().date()
        hour = today.ctime()
        nameSplit = str.split(admin['name'])
        name =  nameSplit[0]
        lastname = nameSplit[1]
        email =admin['email']

        html = """<head>
                <style>
                    table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    }

                    td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                    }

                    tr:nth-child(even) {
                    background-color: #dddddd;
                    }
                </style>
            </head>
            <body>
                <p>Buen d&iacute;a&nbsp;"""+name.capitalize()+"""&nbsp"""+lastname.capitalize()+""".<p>
                <p>Este es un mensaje autom&aacutetico para notificarle sobre los correos
                de prestamo enviados autom&aacuteticamente el d&iacutea """+str(today)+""" por InvIT Emails.</p>
                <p>Los correos enviados son:</p>
                <p>&nbsp;</p>
                <p>"""+htmlMessage+"""</p>
                <p>Atte. InvIT Emails.</p>
                <p>¡Saludos!</p>
                <p>&nbsp;</p>
            </body>"""

        message = {
            'from_email': 'no.reply@laureate.net',
            'from_name': 'Helpdesk IT',
            'headers': {'Reply-To': 'no.reply@laureate.net'},
            'html': html,
            'merge_language': 'mailchimp',
            'subject': 'Return Borrowed Equipment Request',
            'tags': ['password-resets'],
            'to': [{'email': email,
                    'name': name,
                    'type': 'to'}]
        }    

        result = mandrill_client.messages.send(message=message, ip_pool='Main Pool')

        if result[0]['status'] == "sent":
            return {
                "status": 'sent',
            }
        else:
            return {
                "result":"error"
            }

    @staticmethod
    def sendEmails(resultForEmails, admins, supervisor, execution, adminEmailFrec, supervisorEmailFrec):
        acumulatedSentEmails = ''
        result = ''
        allEmails = []
        products = []
        tempIdPage = ''
        todayDate = Email.todayDate();
        expirationDate = ''
        if(resultForEmails):
            for i, item in enumerate(resultForEmails):
                #if is 1 the email should not be send if is 0 an email needs to be sent and compare the expirationDate +1 day with the todays Date
                if(resultForEmails[i]['email_exception'] == 0  and Email.compareDates(int(todayDate)/1000, resultForEmails[i]['updated'])):
                    tempIdPage = resultForEmails[i]['id_signature']
                    try:
                        if(tempIdPage == resultForEmails[i+1]['id_signature']):
                            products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                        else:
                            products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                            result = Email.ss(item,products)
                            allEmails.append(result)
                            acumulatedSentEmails += str(result['message'])
                            products = []
                    except:
                        products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                        result = Email.ss(item,products)
                        allEmails.append(result)
                        acumulatedSentEmails += str(result['message'])
                        products = []


        #send emails to IT admins
        if(adminEmailFrec == 'every time'):
            for i, item in enumerate(admins):
                Email.sendAdminEmails(item, acumulatedSentEmails);
        elif(adminEmailFrec == 'once a week'):
            today = datetime.today().strftime('%A')
            if(today == 'Monday'):
                for i, item in enumerate(admins):
                    Email.sendAdminEmails(item, acumulatedSentEmails);
        elif(adminEmailFrec == 'only manually executions'):
            if(execution == 'manual'):
                for i, item in enumerate(admins):
                    Email.sendAdminEmails(item, acumulatedSentEmails);
        elif(adminEmailFrec == 'only automatically executions'):
            if(execution == 'automatic'):
                for i, item in enumerate(admins):
                    Email.sendAdminEmails(item, acumulatedSentEmails);

        #send emails to IT Supervisor
        #if(supervisorEmailFrec == 'every time'):
        #    for i, item in enumerate(supervisor):
        #        Email.sendAdminEmails(item, acumulatedSentEmails);
        #elif(supervisorEmailFrec == 'once a week'):
        #    today = datetime.today().strftime('%A')
        #    if(today == 'Monday'):
        #         for i, item in enumerate(supervisor):
        #            Email.sendAdminEmails(item, acumulatedSentEmails);
        #elif(supervisorEmailFrec == 'only manually executions'):
        #    if(execution == 'manual'):
        #        for i, item in enumerate(supervisor):
        #            Email.sendAdminEmails(item, acumulatedSentEmails);
        #elif(supervisorEmailFrec == 'only automatically executions'):
        #    if(execution == 'automatic'):
        #        for i, item in enumerate(supervisor):
        #            Email.sendAdminEmails(item, acumulatedSentEmails);
      
        return allEmails
        
    @staticmethod
    def todayDate():
        today = datetime.now();
        todayTimestamp = datetime.timestamp(today)
        return todayTimestamp

    @staticmethod
    def compareDates(todayDate,expirationDate):
        expirationDateObj = datetime.strptime(expirationDate, '%Y-%M-%d')
        expirationDateTimestamp = int(datetime.timestamp(expirationDateObj))/1000
        #print(expirationDateTimestamp)
        #print(todayDate)
        if expirationDateTimestamp < todayDate:
            #print('Return Date Expired')
            return True
        else:
            #print('Return Date NOOO Expired')
            return False 
