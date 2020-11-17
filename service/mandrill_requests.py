import mandrill
import requests
import json
from datetime import datetime
from dateutil.relativedelta import *

API_KEY = 'j3VdGCRj9OsJiY5LZQlT5g'
mandrill_client =  mandrill.Mandrill(API_KEY)
mandrill_link = 'https://mandrillapp.com/api/1.0/'

class Verify():
    data = {
        "key": API_KEY
    }
    responseStruct = requests.post(mandrill_link + 'users/info.json', data = data)
    responseJSON = json.loads(responseStruct.text)

    print(responseJSON['username']);

class Email():
    @staticmethod
    def ss(item,products):
        tempHTML = ""
        loan_date = ""
        id_page = ""
        email = item['email']
        id_page = item['id_signature']
        loan_date = item['updated']
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

                tr:nth-child(even) {
                background-color: #dddddd;
                }
                </style>
                </head>
                <body>
                <p>Buen d&iacute;a<p>
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
                <p>&nbsp;</p>
                <p>&nbsp;</p>
                <p>De antemano, &iexcl;Muchas gracias!.</p>
                <p>Atte. Helpdesk IT.</p>
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
        'to': [{'email': 'julio.zuniga@laureate.net',
                'name': 'Dennis Carcamo',
                'type': 'to'}]
        }

        result = mandrill_client.messages.send(message=message, ip_pool='Main Pool')
        #print (result)

        if result[0]['status'] == "sent":
            return {
                "result": result,
                "id_page": id_page
            }
        else:
            return {
                "result":"error"
            }
       


    @staticmethod
    def sendEmails(resultForEmails):
        result = [];
        products = []
        tempIdPage = ''
        todayDate = Email.todayDate();
        expirationDate = ''
        if(resultForEmails):
            for i, item in enumerate(resultForEmails):
                #if is 1 the email should not be send if is 0 an email needs to be sent and compate the expirationDate +1 day with the todays Date
                if(resultForEmails[i]['email_exception'] == 0  and Email.compareDates(todayDate, resultForEmails[i]['updated'])):
                    tempIdPage = resultForEmails[i]['id_signature']
                    try:
                        if(tempIdPage == resultForEmails[i+1]['id_signature']):
                            products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                        else:
                            products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                            result.append (Email.ss(item,products))
                            products = []
                    except:
                        products.append({'Tag':item['id_product'],'Product Name':item['product_name'],'Serial Number':item['serial_number']})
                        result.append(Email.ss(item,products))
                        products = []
        return result

    @staticmethod
    def todayDate():
        today = datetime.now();
        todayTimestamp = int(datetime.timestamp(today))/1000
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
