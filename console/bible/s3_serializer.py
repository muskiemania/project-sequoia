import traceback
import boto3
import json

from bible import bible

class S3Serializer:

    def __init__(self, config):
        self._config = config

    def serialize(self, bible):

        # need CLI profile
        _profile = self._config['AWS.GENERAL']['cli_profile']

        # need bucket name
        _bucket = self._config['AWS.S3']['bucket']
        # need bucket prefix
        _prefix = self._config['AWS.S3']['prefix']
        # need kms key id
        _kms_key_id = self._config['AWS.S3']['kms_key_id']

        # first write index
        _toc = bible.get_toc()
        s3 = boto3.Session(profile_name=_profile).client('s3')
        s3.put_object(
            Bucket=_bucket,
            Key=f'{_prefix}/_index.json',
            Body=json.dumps(_toc, indent=2, sort_keys=True),
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=_kms_key_id
        )

        # then write pages
        for _chapter in _toc:

            s3.put_object(
                Bucket=_bucket,
                Key=f'{_prefix}/_{_chapter}.json',
                Body=json.dumps(bible.get_chapter(_chapter), indent=2, sort_keys=True),
                ServerSideEncryption='aws:kms',
                SSEKMSKeyId=_kms_key_id
            )

        return True

    def deserialize(self):
        # need CLI profile
        _profile = self._config['AWS.GENERAL']['cli_profile']

        # need bucket name
        _bucket = self._config['AWS.S3']['bucket']
        # need bucket prefix
        _prefix = self._config['AWS.S3']['prefix']
        # need kms key id
        _kms_key_id = self._config['AWS.S3']['kms_key_id']

        # read index
        s3 = boto3.Session(profile_name=_profile).client('s3')
        try:
            _object = s3.get_object(
                Bucket=_bucket,
                Key=f'{_prefix}/_index.json'
            )

            #print('object is:')
            _decoded = _object['Body'].read().decode('utf-8')
            #print(_decoded)
            #print(type(_decoded))
            
            _ix = json.loads(_decoded)
        except:
            traceback.print_exc()
            raise

        _index = {}
        for _chapter in _ix:
            try:
                _object = s3.get_object(
                    Bucket=_bucket,
                    Key=f'{_prefix}/_{_chapter}.json'
                )

                _decoded = _object['Body'].read().decode('utf-8')
                _index[_chapter] = json.loads(_decoded)
            except:
                raise

        return bible.Bible(_index)

