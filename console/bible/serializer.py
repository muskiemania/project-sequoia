import boto3
import json

class BibleSerializer:

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
        _ix = bible.get_index()
        s3 = boto3.Session(profile_name=_profile).client('s3')
        s3.put_object(
            Bucket=_bucket,
            Key=f'{_prefix}/_index.json',
            Body=json.dumps(_ix),
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=_kms_key_id
        )

        # then write pages
        for _page in _ix:

            s3.put_object(
                Bucket=_bucket,
                Key=f'{_prefix}/_{_page}.json',
                Body=json.dumps(bible.get_persons(_page)),
                ServerSideEncryption='aws:kms',
                SSEKMSKeyId=_kms_key_id
            )

        return True
