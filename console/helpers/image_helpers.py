import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class ImageHelpers:

    def __init__(self):
        self._config = None

    def init(self, _config):
        print(_config)
        self._config = _config
        print(self._config)
        return self

    def get_presigned_url(self, _path):
        # need CLI profile
        _profile = self._config['AWS.GENERAL']['cli_profile']

        # need bucket name
        _bucket = self._config['AWS.S3']['bucket']
        # need bucket prefix
        _prefix = self._config['AWS.S3']['prefix']

        # first write index
        s3 = boto3.Session(profile_name=_profile).client('s3', config=Config(signature_version='s3v4'))
        
        try:
            return s3.generate_presigned_url('get_object', Params={'Bucket': _bucket, 'Key': f'{_prefix}/images/{_path}'}, ExpiresIn=300)
        except ClientError as e:
            print(f'bucket: {_bucket}')
            print(f'key: {_prefix}/images/{_path}')

            traceback.print_exc()
            return None
