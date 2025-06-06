import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import pandas as pd
import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import the modules to be tested/mocked
from logo_scraper import LogoScraper, parse_arguments, update_config_from_args
from config import CONFIG as GlobalAppConfig # Import the actual config for default values

# Default mock config values, can be overridden in specific tests
BASE_MOCK_CONFIG = GlobalAppConfig.copy() # Start with actual defaults
MOCK_CONFIG_OVERRIDE = {
    'INPUT_FILE': 'test_input.xlsx',
    'OUTPUT_FOLDER': 'test_output_logos',
    'TEMP_FOLDER': 'test_temp_data',
    'BATCH_SIZE': 2,
    'LOG_LEVEL': 'INFO',
    'MAX_PROCESSES': 2,
    'TOP_N': None,
    'filters': {},
    'tpid_filter': [],
    'LOG_FILENAME': 'test_scraper.log',
    'FAILED_DOMAINS_CACHE_FILE': 'test_failed_domains.json',
    'PROGRESS_FILE': 'test_progress.json',
    'ENRICHED_FILENAME_PREFIX': 'test_enriched_',
    'OUTPUT_SIZE': 256, # For ConfigValidator via LogoScraper
    'MIN_SOURCE_SIZE': 50,
    'CLEARBIT_RATE_LIMIT': 1,
    'USER_AGENT': 'Test User Agent',
    'REQUEST_TIMEOUT': 10,
    'RETRY_DELAY': 1.0,
    'MAX_RETRIES': 3,
    # Add any other keys that ConfigValidator might check from the actual config
    'CLEARBIT_BASE_URL': 'http://fakeclearbit.com',
    'PNG_QUALITY': 90,
    'MAX_UPSCALING_RATIO': 8,
}
BASE_MOCK_CONFIG.update(MOCK_CONFIG_OVERRIDE)


class TestLogoScraper(unittest.TestCase):

    def _get_mock_config(self):
        # Returns a fresh copy for each test to avoid interference
        return BASE_MOCK_CONFIG.copy()

    @patch('logo_scraper.setup_logging')
    @patch('logo_scraper.ConfigValidator')
    @patch('logo_scraper.ProgressTracker')
    @patch('os.makedirs')
    @patch('logo_scraper.LogoScraper._load_failed_domains_cache') # Patching the method on the class
    def setUp(self, mock_load_cache, mock_os_makedirs, mock_progress_tracker, mock_config_validator, mock_setup_logging):
        # This setUp will mock dependencies for ALL tests.
        # If a test needs different behavior, it can re-patch within the test method.
        self.mock_config = self._get_mock_config()

        # Configure mocks
        mock_config_validator_instance = MagicMock()
        mock_config_validator_instance.validate.return_value = True
        mock_config_validator.return_value = mock_config_validator_instance
        mock_load_cache.return_value = set() # Default: no failed domains loaded

        # Apply the mock_config to the CONFIG imported by logo_scraper
        # This is the primary way to control config for the LogoScraper instance
        self.config_patcher = patch.dict('logo_scraper.CONFIG', self.mock_config)
        self.mocked_logo_scraper_config = self.config_patcher.start()

        # Instantiate LogoScraper - this will use the patched CONFIG
        # and the mocks provided to setUp
        self.scraper = LogoScraper(
            output_folder=self.mock_config['OUTPUT_FOLDER'],
            batch_size=self.mock_config['BATCH_SIZE']
        )
        
        # Store mocks if needed for assertions in specific tests
        self.mock_setup_logging = mock_setup_logging
        self.mock_config_validator = mock_config_validator
        self.mock_config_validator_instance = mock_config_validator_instance
        self.mock_progress_tracker = mock_progress_tracker
        self.mock_os_makedirs = mock_os_makedirs
        self.mock_load_cache = mock_load_cache


    def tearDown(self):
        self.config_patcher.stop() # Important to stop the patch

    def test_initialization(self):
        """Test that LogoScraper initializes correctly."""
        self.mock_os_makedirs.assert_any_call(self.mock_config['OUTPUT_FOLDER'], exist_ok=True)
        self.mock_os_makedirs.assert_any_call(self.mock_config['TEMP_FOLDER'], exist_ok=True)
        self.mock_setup_logging.assert_called_once_with(self.mock_config['TEMP_FOLDER'], self.mock_config['LOG_FILENAME'])
        self.mock_config_validator.assert_called_once_with(self.mocked_logo_scraper_config) # Check it's called with the patched CONFIG
        self.mock_config_validator_instance.validate.assert_called_once()
        self.mock_load_cache.assert_called_once() # Check that _load_failed_domains_cache was called
        self.assertIsNotNone(self.scraper.progress) # ProgressTracker should be initialized

    @patch('builtins.open', new_callable=mock_open, read_data='["domain1.com", "domain2.com"]')
    @patch('json.load')
    def test_load_failed_domains_cache_exists(self, mock_json_load, mock_file_open):
        """Test loading failed domains from an existing cache file."""
        mock_json_load.return_value = ["domain1.com", "domain2.com"]
        # We need to call it directly as setUp already called it once.
        # For a clean test, one might instantiate scraper here instead of setUp for some tests.
        failed_domains = self.scraper._load_failed_domains_cache() 
        expected_path = os.path.join(self.mock_config['TEMP_FOLDER'], self.mock_config['FAILED_DOMAINS_CACHE_FILE'])
        mock_file_open.assert_called_with(expected_path, 'r')
        mock_json_load.assert_called_once()
        self.assertEqual(failed_domains, {"domain1.com", "domain2.com"})

    @patch('os.path.exists', return_value=False)
    def test_load_failed_domains_cache_not_exists(self, mock_path_exists):
        """Test loading failed domains when cache file does not exist."""
        failed_domains = self.scraper._load_failed_domains_cache()
        self.assertEqual(failed_domains, set())

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_failed_domains_cache(self, mock_json_dump, mock_file_open):
        """Test saving failed domains to cache."""
        self.scraper.failed_domains = {"domain1.com", "domain3.com"}
        self.scraper._save_failed_domains_cache()
        expected_path = os.path.join(self.mock_config['TEMP_FOLDER'], self.mock_config['FAILED_DOMAINS_CACHE_FILE'])
        mock_file_open.assert_called_with(expected_path, 'w')
        mock_json_dump.assert_called_once_with(list(self.scraper.failed_domains), mock_file_open())

    @patch('os.remove')
    @patch('shutil.rmtree')
    @patch('os.listdir')
    @patch('os.path.join', side_effect=lambda *args: os.sep.join(args)) # Mock join to behave normally
    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_clean_temporary_data_force_clean(self, mock_exists, mock_isdir, mock_isfile, mock_join, mock_listdir, mock_rmtree, mock_remove):
        """Test clean_temporary_data with force_clean=True."""
        mock_exists.return_value = True # Temp folder exists
        mock_listdir.return_value = ['file1.txt', 'subdir']
        mock_isfile.side_effect = lambda path: path.endswith('.txt')
        mock_isdir.side_effect = lambda path: path.endswith('subdir')

        self.scraper.clean_temporary_data(force_clean=True)

        temp_folder_path = self.mock_config['TEMP_FOLDER']
        mock_listdir.assert_called_once_with(temp_folder_path)
        mock_remove.assert_called_once_with(os.path.join(temp_folder_path, 'file1.txt'))
        mock_rmtree.assert_called_once_with(os.path.join(temp_folder_path, 'subdir'))
        # Check if temp folder is recreated
        self.mock_os_makedirs.assert_any_call(temp_folder_path, exist_ok=True)


    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.concat')
    @patch('pandas.DataFrame.to_excel') # For saving enriched data
    def test_save_enriched_data_success(self, mock_to_excel, mock_pd_concat, mock_file):
        """Test saving enriched data successfully."""
        mock_df1 = pd.DataFrame({'A': [1]})
        mock_df2 = pd.DataFrame({'A': [2]})
        self.scraper.enriched_data = [mock_df1, mock_df2]
        
        # Mock os.path.dirname to control the output path construction
        with patch('os.path.dirname', return_value='mock_input_dir'):
            self.scraper.save_enriched_data()

        mock_pd_concat.assert_called_once_with(self.scraper.enriched_data, ignore_index=True)
        # Path construction is complex due to timestamp, so we check if to_excel was called.
        # A more specific check would involve asserting the path starts with the expected prefix.
        self.assertTrue(mock_to_excel.call_args[0][0].startswith(os.path.join('mock_input_dir', self.mock_config['ENRICHED_FILENAME_PREFIX'])))


    @patch('logo_scraper.InputDataService')
    def test_get_input_data(self, MockInputDataService):
        """Test getting input data."""
        mock_service_instance = MockInputDataService.return_value
        mock_df = pd.DataFrame({'tpid': ['123'], 'crmaccountname': ['TestCo']})
        mock_service_instance.get_data.return_value = mock_df
        
        # Test without TPID filter initially
        self.mocked_logo_scraper_config['tpid_filter'] = [] # Ensure no tpid filter for this part
        
        df = self.scraper.get_input_data()
        
        mock_service_instance.get_data.assert_called_once_with(
            filters=self.mock_config.get('filters'),
            top_n=self.mock_config.get('TOP_N')
        )
        pd.testing.assert_frame_equal(df, mock_df)

        # Test with TPID filter
        self.mocked_logo_scraper_config['tpid_filter'] = ['123']
        # Re-instantiate scraper or re-patch its config if necessary, or ensure get_input_data re-reads from logo_scraper.CONFIG
        # For this test, let's assume get_input_data directly uses the module level CONFIG which is patched by self.mocked_logo_scraper_config
        
        df_filtered = self.scraper.get_input_data() # Call again with updated config
        
        # get_data is called again, then pandas filters it.
        # The mock_service_instance.get_data is for the initial load.
        # The TPID filtering happens *after* data is returned from the service.
        expected_df_filtered = mock_df[mock_df['tpid'].isin(['123'])]
        pd.testing.assert_frame_equal(df_filtered, expected_df_filtered)


    def test_filter_unprocessed_companies(self):
        """Test filtering of unprocessed companies."""
        df = pd.DataFrame({
            'tpid': ['1', '2', '3', '4'],
            'name': ['A', 'B', 'C', 'D']
        })
        self.scraper.progress.progress = {'completed': ['1'], 'failed': ['2']}
        
        unprocessed_df = self.scraper._filter_unprocessed_companies(df.copy()) # Pass a copy
        
        expected_df = pd.DataFrame({
            'tpid': ['3', '4'],
            'name': ['C', 'D']
        }, index=[2,3]) # Pandas keeps original index after boolean indexing
        pd.testing.assert_frame_equal(unprocessed_df.reset_index(drop=True), expected_df.reset_index(drop=True))


    @patch('logo_scraper.LogoScraper.get_input_data')
    @patch('logo_scraper.LogoScraper._filter_unprocessed_companies')
    @patch('logo_scraper.LogoScraper.process_batch') # Mocking the instance method
    def test_process_companies_simple_run(self, mock_process_batch_method, mock_filter_unprocessed, mock_get_input_data):
        """Test a simple run of process_companies."""
        input_df = pd.DataFrame({'tpid': ['101', '102'], 'crmaccountname': ['CompA', 'CompB']})
        unprocessed_df = pd.DataFrame({'tpid': ['101', '102'], 'crmaccountname': ['CompA', 'CompB']})
        
        mock_get_input_data.return_value = input_df
        mock_filter_unprocessed.return_value = unprocessed_df
        
        # Mock results from process_batch (the method in LogoScraper)
        # This method should return (successful_in_batch, total_in_batch, enriched_df_batch)
        enriched_results_df = pd.DataFrame({
            'TPID': ['101', '102'], 
            'LogoGenerated': [True, False],
            'LogoSource': ['Clearbit', 'Failed (Error)']
        })
        mock_process_batch_method.return_value = (1, 2, enriched_results_df)

        self.scraper.process_companies()

        mock_get_input_data.assert_called_once()
        mock_filter_unprocessed.assert_called_once_with(input_df)
        mock_process_batch_method.assert_called_once() # Since BATCH_SIZE=2, one batch
        
        # Check progress marking
        self.scraper.progress.mark_completed.assert_called_with('101')
        self.scraper.progress.mark_failed.assert_called_with('102')
        self.assertEqual(len(self.scraper.enriched_data), 1) # One batch's enriched data

    @patch('logo_scraper.process_batch') # Mock the imported utility function
    def test_scraper_process_batch_method(self, mock_util_process_batch):
        """Test the LogoScraper's process_batch method."""
        batch_df = pd.DataFrame({'tpid': ['1'], 'name': ['TestCo']})
        enriched_df_mock = pd.DataFrame({'TPID': ['1'], 'LogoGenerated': [True], 'LogoSource': ['Test']})
        mock_util_process_batch.return_value = (1, 1, enriched_df_mock)

        # Temporarily set total_companies for logging within _log_batch_progress_summary
        self.scraper.total_companies = 1 
        
        successful, total, result_enriched_df = self.scraper.process_batch(batch_df, 1, 1)

        mock_util_process_batch.assert_called_once_with(
            companies_df=batch_df,
            output_folder=self.scraper.output_folder,
            temp_folder=self.scraper.temp_folder,
            batch_idx=1,
            total_batches=1
        )
        self.assertEqual(successful, 1)
        self.assertEqual(total, 1)
        self.assertEqual(self.scraper.total_successful, 1)
        self.assertEqual(self.scraper.total_failed, 0)
        self.assertIn(enriched_df_mock, self.scraper.enriched_data)
        pd.testing.assert_frame_equal(result_enriched_df, enriched_df_mock)


    @patch('logo_scraper.LogoScraper._save_failed_domains_cache')
    @patch('logo_scraper.LogoScraper.save_enriched_data')
    def test_cleanup(self, mock_save_enriched, mock_save_failed_domains):
        """Test the cleanup method."""
        self.scraper.cleanup()
        mock_save_failed_domains.assert_called_once()
        mock_save_enriched.assert_called_once()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
