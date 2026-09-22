from app.core.config import DEFAULT_DATA_DIR, get_settings


def test_default_data_dir_is_repo_data_folder(monkeypatch):
    monkeypatch.delenv("SNACKOVERFLOW_DATA_DIR", raising=False)
    settings = get_settings()
    assert settings.data_dir == DEFAULT_DATA_DIR
    assert settings.restaurants_file == DEFAULT_DATA_DIR / "restaurants.json"


def test_data_dir_can_be_overridden_with_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("SNACKOVERFLOW_DATA_DIR", str(tmp_path))
    settings = get_settings()
    assert settings.data_dir == tmp_path
    assert settings.restaurants_file == tmp_path / "restaurants.json"
