import sys
import os
from pathlib import Path
from config import Config
from configparser import ConfigParser

# Add the parent directory to the sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Import the Config class


def test_config_variables():
    config = Config(ConfigParser())
    # Construct the path to the config_test.ini file under the tests directory
    config_file_path = Path(__file__).parent / 'config_test.ini'
    config.config_file = config_file_path
    # Assertion tests
    assert config.config_file == config_file_path
    assert isinstance(config.configparser, ConfigParser)
    assert config.twitch_token == ''  # Set your test token here
    assert config.twitch_prefix == ''  # Set your test prefix here
    assert config.twitch_initial_channels == []  # Set your test initial channels here
    assert config.welcome_cooldown == 60


if __name__ == "__main__":
    test_config_variables()
    # Call other test functions here if needed
