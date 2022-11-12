import register.handler as handler
from unittest.mock import patch

@patch('register.controller.RegistrationController.register')
def test_handler_ok(mock_register):
    # arrange
    event = {}
    context = {}

    # act
    actual = handler.handler(event, context)

    # assert
    assert actual['statusCode'] == 200
    assert actual['body'] == 'OK'
    mock_register.assert_called_once_with(event)
