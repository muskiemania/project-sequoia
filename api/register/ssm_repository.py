import boto3
import json

client = boto3.client('ssm')

class SSMRepository:

    def __init__(self):
        pass

    def write(self, secret_id, secret_json):
        client.put_secret_value(
            SecretId=secret_id,
            SecretString=json.dumps(secret_json)
        )

        return True
