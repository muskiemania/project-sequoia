from register.service import RegistrationService
from register.ssm_repository import SSMRepository
from register.s3_repository import S3Repository
from unittest.mock import patch, Mock

def test_constructor_ok():
    # arrange
    # act
    service = RegistrationService()

    # assert
    assert isinstance(service.ssm, SSMRepository)
    assert isinstance(service.s3, S3Repository)

@patch('helpers.env.EnvConfig.name')
def test_register_ok(mock_env_name):
    # arrange
    service = RegistrationService()
    name = 'name'
    password = 'password'

    pub = 'pub'
    pvt = 'pvt'
    mock_generate = Mock()
    mock_generate.return_value = (pub, pvt)
    service._generate_keys = mock_generate

    mock_ssm = Mock()
    mock_ssm.write.return_value = True
    service.ssm = mock_ssm

    mock_s3 = Mock()
    mock_s3.save.return_value = True
    service.s3 = mock_s3
    
    mock_env = Mock()
    mock_env.name = 'test'
    service.env = mock_env

    # act
    actual = service.register(name, password)

    # assert
    assert actual is True
    mock_generate.assert_called_once()
    mock_ssm.write.assert_called_once_with(f'sequoia/test/{name}/keys', {'public': pub, 'private': pvt, 'password': password})
    mock_s3.save.assert_called_once_with(
        'project-sequoia',
        'test/data',
        f'{name}.json',
        {'name': name, 'fingerprint': 'encrypted name', 'body': {}}
    )
