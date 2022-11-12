import logging
from .service import RegistrationService
from .validation_service import ValidationService

class RegistrationController:

    def __init__(self):
        self.service = RegistrationService()
        self.validation = ValidationService()

    def register(self, event):

        self.validation.validate(event)

        logging.info('event validated OK')

        name = ''
        password = ''

        self.service.register(name, password)

        logging.info(f'{name} registration OK')

        return True
