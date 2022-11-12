import logging
from .service import RegistrationService
from .validation_service import ValidationService

class RegistrationController:

    def __init__(self):
        self.service = RegistrationService()
        self.validation = ValidationService()

    def register(self, event):

        if not self.validation.validate(event):
            return False

        logging.info('event validated OK')

        name = ''
        password = ''

        if self.service.register(name, password):
            logging.info(f'{name} registration OK')
            return True
        
        return False
