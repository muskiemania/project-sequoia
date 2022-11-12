import logging
from .s3_repository import S3Repository
from .ssm_repository import SSMRepository
from helpers import env
from OpenSSL import crypto
import base64

class RegistrationService:

    def __init__(self):
        self.ssm = SSMRepository()
        self.s3 = S3Repository()
    
    def register(self, name, password):

        # create public and private keys
        (pub, pvt) = self._generate_keys()
        logging.info('keys created')

        # store in SSM
        self.ssm.write(f'sequoia/{env.name}/{name}/keys', {'public': pub, 'private': pvt, 'password': password})
        logging.info('keys stored')

        # create default file
        # add metadata, sign with key
        # load into S3
        _file = {
            'name': name,
            'fingerprint': 'encrypted name',
            'body': {}
        }
        self.s3.save(f'project-sequoia', f'{env.name}/data', f'{name}.json', _file)
        logging.info('file written')

        return True

    def _generate_keys(self):
        pk = crypto.PKey()
        pk.generate_key(crypto.TYPE_RSA, 2048)

        pub = base64.b64encode(crypto.dump_publickey(crypto.FILETYPE_PEM, pk))
        pvt = base64.b64encode(crypto.dump_privatekey(crypto.FILETYPE_PEM, pk))

        return (pub, pvt)


