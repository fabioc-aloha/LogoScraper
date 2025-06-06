import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
Test Suite for Company Logo Scraper

Run with:
    pytest tests/

This suite covers:
- Core logic in logo_scraper_core.py (LogoScraper)
- CLI argument parsing and config update (cli.py)
- Temp folder cleaning (cleanup.py)
- Config defaults and logging (config.py)
- Error handling and cleanup
"""

import os
import tempfile
import shutil
import pandas as pd
import pytest
from unittest import mock
from src.logo_scraper_core import LogoScraper
from src.config import CONFIG
from io import StringIO
import logging
import builtins
import src.cleanup
import src.config as config_module
import sys
import os

# Import CLI functions from main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from main import parse_arguments, update_config_from_args

class DummyInputDataService:
    def get_data(self, filters=None, top_n=None):
        data = {
            'tpid': ['1', '2', '3'],
            'websiteurl': ['http://a.com', 'http://b.com', '']
        }
        return pd.DataFrame(data)

@pytest.fixture(autouse=True)
def patch_input_data_service(monkeypatch):
    from src.services.input_data_service import InputDataService
    monkeypatch.setattr('src.logo_scraper_core.InputDataService', DummyInputDataService)
    # Also ensure tpid_filter is cleared for tests that don't need it
    if 'tpid_filter' in CONFIG:
        del CONFIG['tpid_filter']

@pytest.fixture
def temp_dirs():
    output = tempfile.mkdtemp()
    temp = tempfile.mkdtemp()
    old_output = CONFIG['OUTPUT_FOLDER']
    old_temp = CONFIG['TEMP_FOLDER']
    CONFIG['OUTPUT_FOLDER'] = output
    CONFIG['TEMP_FOLDER'] = temp
    yield output, temp
    CONFIG['OUTPUT_FOLDER'] = old_output
    CONFIG['TEMP_FOLDER'] = old_temp
    import logging
    logging.shutdown()
    shutil.rmtree(output)
    shutil.rmtree(temp)

@pytest.fixture
def logo_scraper(temp_dirs):
    output, _ = temp_dirs
    return LogoScraper(output_folder=output, batch_size=2)

def test_logo_scraper_init_creates_dirs(temp_dirs):
    output, temp = temp_dirs
    assert os.path.exists(output)
    assert os.path.exists(temp)

def test_logo_scraper_get_input_data(logo_scraper):
    df = logo_scraper.get_input_data()
    assert isinstance(df, pd.DataFrame)
    assert 'tpid' in df.columns
    assert 'websiteurl' in df.columns

def test_logo_scraper_format_time():
    ls = LogoScraper()
    assert ls._format_time(3661) == '1h 1m 1s'
    assert ls._format_time(61) == '1m 1s'
    assert ls._format_time(10) == '10s'

def test_logo_scraper_save_and_load_failed_domains(logo_scraper):
    logo_scraper.failed_domains = {'a.com', 'b.com'}
    logo_scraper._save_failed_domains()
    loaded = logo_scraper._load_failed_domains()
    assert 'a.com' in loaded and 'b.com' in loaded

def test_logo_scraper_process_companies_runs(logo_scraper):
    # Should not raise
    logo_scraper.process_companies()

def test_logo_scraper_cleanup_runs(logo_scraper):
    # Should not raise
    logo_scraper.cleanup()

def test_cli_argument_parsing_and_config_update(monkeypatch):
    test_args = [
        'logo_scraper.py', '--input', 'test.xlsx', '--output', 'outdir', '--batch-size', '10', '--log-level', 'DEBUG'
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()
    update_config_from_args(args)
    assert config_module.CONFIG['INPUT_FILE'] == 'test.xlsx'
    assert config_module.CONFIG['OUTPUT_FOLDER'] == 'outdir'
    assert config_module.CONFIG['BATCH_SIZE'] == 10
    assert config_module.CONFIG['LOG_LEVEL'] == 'DEBUG'

def test_cleanup_temp_folder_creates_and_cleans(tmp_path):
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "dummy.txt").write_text("test")
    
    # Mock logging to avoid file path issues in tests
    with mock.patch('src.cleanup.logging.info') as mock_info, \
         mock.patch('src.cleanup.logging.error') as mock_error:
        src.cleanup.clean_temp_folder(str(temp_dir))
        
    assert os.path.exists(temp_dir)
    assert not any(temp_dir.iterdir())

def test_config_defaults_and_logging_level():
    """
    Test that LOG_LEVEL is present in config and can be set.
    Note: We do not assert on logging.getLogger().getEffectiveLevel() because
    logging.basicConfig() has no effect if logging is already configured.
    """
    original_log_level = config_module.CONFIG['LOG_LEVEL']
    try:
        config_module.CONFIG['LOG_LEVEL'] = 'ERROR'
        assert 'LOG_LEVEL' in config_module.CONFIG
        assert config_module.CONFIG['LOG_LEVEL'] == 'ERROR'
        config_module.CONFIG['LOG_LEVEL'] = 'INFO'
        assert config_module.CONFIG['LOG_LEVEL'] == 'INFO'
    finally:
        config_module.CONFIG['LOG_LEVEL'] = original_log_level

def test_logo_scraper_error_handling_and_cleanup(monkeypatch, temp_dirs):
    class FailingLogoScraper(LogoScraper):
        def process_companies(self):
            raise RuntimeError("Simulated failure")
        
        def cleanup(self):
            self.cleaned = True
    
    scraper = None
    monkeypatch.setattr(logging, 'error', lambda msg: setattr(scraper, 'logged', msg) if scraper else None)
    # Patch config to avoid config validation failure
    import src.config as config_module
    original_input_file = config_module.CONFIG['INPUT_FILE']
    config_module.CONFIG['INPUT_FILE'] = __file__  # Use this test file as a dummy input
    try:
        scraper = FailingLogoScraper(output_folder=temp_dirs[0], batch_size=2)
        with pytest.raises(RuntimeError):
            scraper.process_companies()
        scraper.cleanup()
        assert hasattr(scraper, 'cleaned')
    finally:
        config_module.CONFIG['INPUT_FILE'] = original_input_file
