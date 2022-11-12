import logging
from register.controller import RegistrationController
from dotenv import load_dotenv

def handler(event, context):

    logging.info('handler start')

    load_dotenv()

    controller = RegistrationController()

    if controller.register(event):
        return {
            'statusCode': 200,
            'body': 'OK'
        }

    return {
        'statusCode': 500,
        'body': 'ERROR'
    }
