import boto3

class BibleSerializer:

    def __init__(self, config):
        self._config = config

    def serialize(self, bible):

        # need CLI profile

        # need bucket name
        _bucket = self._config['AWS.S3']['bucket_name']
        # need bucket prefix
        _prefix = self._config['AWS.S3']['prefix']
        # need kms key id
        _kms_key_id = self._config['AWS.S3']['kms_key_id']

        # first write index
        _ix = bible.get_pages()
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=_bucket,
            Key=f'{_prefix}/_index.json',
            Body=json.dumps(bible.get_pages()),
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=_kms_key_id
        )

        # then write pages
        for _page in bible.get_pages():

            s3.put_object(
                Bucket=_bucket,
                Key=f'{_prefix}/_{page}.json',
                Body=json.dumps(bible.get_persons(_page)),
                ServerSideEncryption='aws:kms',
                SSEKMSKeyId=_kms_key_id
            )

        return True
