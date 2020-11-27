import base64
import json
import boto3

from bible import bible

class LocalSerializer:

    def __init__(self, config):
        self._config = config

    def serialize(self, bible):

        # need CLI profile
        _profile = self._config['AWS.GENERAL']['cli_profile']

        # need local filename
        _file = self._config['LOCAL']['filename']

        # need kms key id
        _kms_key_id = self._config['AWS.KMS']['kms_key_id']

        # encode index data
        kms = boto3.Session(profile_name=_profile).client('kms')
        ciphertext = kms.encrypt(
            KeyId=_kms_key_id,
            Plaintext=json.dumps(bible._index).encode('utf-8')
        )

        # write encoded to local file
        with open(_file, 'w') as _local:
            _local.write(base64.b64encode(ciphertext['CiphertextBlob']).decode('ascii'))

        return True

    def deserialize(self):

        # need CLI profile
        _profile = self._config['AWS.GENERAL']['cli_profile']

        # need local filename
        _file = self._config['LOCAL']['filename']

        # need kms key id
        _kms_key_id = self._config['AWS.KMS']['kms_key_id']

        # read encoded data from local file
        kms = boto3.Session(profile_name=_profile).client('kms')
        with open(_file, 'r') as _local:
            _encrypted = _local.read()
            plaintext = kms.decrypt(
                CiphertextBlob=bytes(base64.b64decode(_encrypted))
            )

        return bible.Bible(json.loads(plaintext['Plaintext']))
