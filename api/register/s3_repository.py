import boto3

s3 = boto3.resource('s3')

class S3Repository:

    def __init__(self):
        pass

    def save(self, bucket_name, prefix, key, _object):
        bucket = s3.Bucket(bucket_name)

        bucket.put_object(
            Body=json.dumps(_object).encode('utf-8'),
            Key=[prefix, key].join('/'),
            ContentType='text/json'
        )

        return True
