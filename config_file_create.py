#This is the configuration file, make sure you know what are you doing before changing something. 

from configparser import ConfigParser

config = ConfigParser()

#for the Data Base
config['dataBase'] = {
    'DATA_BASE_HOST' : '127.0.0.1',
    'DATA_BASE_PORT' :'5432',
    'DATA_BASE_USER' :'postgres',
    'DATA_BASE_PASSWORD' :'!AmxLOL1',
    'DATA_BASE_NAME' :'InvIT'
}

#Group of persons that might get a resume of all emails sent
config['IT_ADMINISTRATORS_EMAILS'] = {
    'Dennis Carcamo':'dennis.carcamo@laureate.net',
    'Carlos Ramirez':'carlos.ramirez@laureate.net',
    'Julio Zuniga':'julio.zuniga@laureate.net',
    'Oscar Nagera':'oscar.nagera@laureate.net'}

#The email of the current IT Supervisor.
config['IT_SUPERVISOR_EMAIL'] = {'Kewyn Medina':'kewyn.medina@laureate.net'}

with open('./configurations.ini', 'w') as configFile:
    config.write(configFile)