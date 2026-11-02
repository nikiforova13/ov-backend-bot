from ov_backend_bot.config import Settings
from ov_backend_bot.sheets import service_account_info


def _google_credentials() -> dict[str, str]:
    return {
        "google_project_id": "ourstudentstables",
        "google_private_key_id": "key-id",
        "google_private_key": "-----BEGIN PRIVATE KEY-----\\nsecret\\n-----END PRIVATE KEY-----\\n",
        "google_client_email": "bot@example.iam.gserviceaccount.com",
        "google_client_id": "123",
        "google_client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot",
    }


def test_settings_read_spreadsheet_url() -> None:
    settings = Settings(
        bot_token="test-token",
        google_spreadsheet_id="https://docs.google.com/spreadsheets/d/sheetId/edit#gid=0",
        google_worksheet_name="",
        _env_file=None,
        **_google_credentials(),
    )

    assert settings.google_spreadsheet_id == "sheetId"
    assert settings.google_worksheet_name is None
    assert settings.uses_google_sheet() is True


def test_blank_google_sheet_settings_are_disabled() -> None:
    settings = Settings(
        bot_token="test-token",
        google_spreadsheet_id="",
        google_project_id="",
        google_private_key="",
        _env_file=None,
    )

    assert settings.google_spreadsheet_id is None
    assert settings.google_private_key is None
    assert settings.uses_google_sheet() is False


def test_private_key_newlines_are_restored() -> None:
    settings = Settings(
        bot_token="test-token",
        _env_file=None,
        **_google_credentials(),
    )
    assert settings.google_private_key is not None

    private_key = settings.google_private_key.get_secret_value()
    info = service_account_info(settings)

    assert private_key == "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----\n"
    assert info["private_key"] == private_key
    assert info["token_uri"] == "https://oauth2.googleapis.com/token"
    assert info["client_email"] == "bot@example.iam.gserviceaccount.com"