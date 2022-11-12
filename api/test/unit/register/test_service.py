from register.service import RegistrationService
from register.ssm_repository import SSMRepository
from register.s3_repository import S3Repository
from unittest.mock import patch

def test_constructor_ok():
    # arrange
    # act
    service = RegistrationService()

    # assert
    assert isinstance(service.ssm, SSMRepository)
    assert isinstance(service.s3, S3Repository)

@patch('register.service.RegistrationService._generate_keys')
@patch('register.service.RegistrationService.ssm.write')
@patch('register.service.RegistrationService.s3.save')
@patch('helpers.env.name', 'test')
def test_register_ok(mock_env_name, mock_save, mock_write, mock_generate):
    # arrange
    service = RegistrationService()
    name = 'name'
    password = 'password'

    pub = 'pub'
    pvt = 'pvt'
    mock_generate.return_value = (pub, pvt)

    # act
    actual = service.register(name, password)

    # assert
    assert actual is True
    mock_generate.assert_called_once()
    mock_write.assert_called_once_with(f'sequoia/test/{name}/keys', {'public': pub, 'private': pvt, 'password': password})
    mock_save.assert_called_once_with(
        'project-sequoia',
        'test/data',
        f'{name}.json',
        {'name': name, 'fingerprint': 'encrypted name', 'body': {}}
    )
