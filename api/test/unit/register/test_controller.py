from register.controller import RegistrationController
from unittest.mock import patch

@patch('register.validation_service.ValidationService.validate')
@patch('register.service.RegistrationService.register')
def test_register_validation_failure(mock_register, mock_validate):
    # arrange
    controller = RegistrationController()
    event = {}
    mock_validate.return_value = False

    # act
    actual = controller.register(event)

    # assert
    assert actual is False
    mock_validate.assert_called_once_with(event)
    mock_register.assert_not_called()

@patch('register.validation_service.ValidationService.validate')
@patch('register.service.RegistrationService.register')
def test_register_service_ok(mock_register, mock_validate):
    # arrange
    controller = RegistrationController()
    event = {}
    mock_validate.return_value = True
    mock_register.return_value = True

    # act
    actual = controller.register(event)

    # assert
    assert actual is True
    mock_validate.assert_called_once_with(event)
    mock_register.assert_called_once_with('', '')


@patch('register.validation_service.ValidationService.validate')
@patch('register.service.RegistrationService.register')
def test_register_service_error(mock_register, mock_validate):
    # arrange
    controller = RegistrationController()
    event = {}
    mock_validate.return_value = True
    mock_register.return_value = False

    # act
    actual = controller.register(event)

    # assert
    assert actual is False
    mock_validate.assert_called_once_with(event)
    mock_register.assert_called_once_with('', '')
