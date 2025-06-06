import unittest
import argparse
from unittest.mock import patch

from config import CONFIG as GlobalConfig
import logo_scraper

class TestUpdateConfigFromArgs(unittest.TestCase):
    def test_update_config_from_args_overrides(self):
        base_config = GlobalConfig.copy()
        with patch.dict('logo_scraper.CONFIG', base_config, clear=True):
            args = argparse.Namespace(
                input='cli_input.xlsx',
                output='cli_output',
                temp=None,
                batch_size=5,
                log_level=None,
                max_processes=None,
                top=None,
                clean=False,
                filter=['country=US'],
                tpid=None
            )
            logo_scraper.update_config_from_args(args)

            self.assertEqual(logo_scraper.CONFIG['INPUT_FILE'], 'cli_input.xlsx')
            self.assertEqual(logo_scraper.CONFIG['OUTPUT_FOLDER'], 'cli_output')
            self.assertEqual(logo_scraper.CONFIG['BATCH_SIZE'], 5)
            self.assertIn('filters', logo_scraper.CONFIG)
            self.assertEqual(logo_scraper.CONFIG['filters']['country'], 'US')

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
