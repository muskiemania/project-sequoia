from bible import s3_serializer
from bible import local_serializer 

class SerializerFactory:

    @staticmethod
    def generate(serializer_type, config):

        if serializer_type == 's3':
            return s3_serializer.S3Serializer(config)

        if serializer_type == 'local':
            return local_serializer.LocalSerializer(config)

        raise ValueError(f'unknown serializer: {serializer_type}')
