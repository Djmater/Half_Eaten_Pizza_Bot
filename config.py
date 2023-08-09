from pathlib import Path


class Config:
    def __init__(self, cp):
        self.config_file = Path('config.ini')
        self.configparser = cp
        self.twitch_token = ''
        self.twitch_prefix = ''
        self.twitch_initial_channels = []
        self.welcome_cooldown = 60

    def read_config_file(self):

        if not self.config_file.is_file():
            print("No file")
            self.make_config_file()
            self.write_config_file()

        self.configparser.read(self.config_file)

        # Read the Twitch settings
        self.twitch_token = self.configparser.get('Twitch', 'token')
        self.twitch_prefix = self.configparser.get('Twitch', 'prefix')
        self.twitch_initial_channels.append(self.configparser.get('Twitch', 'initial_channels'))
        try:
            self.welcome_cooldown = float(self.configparser.get('Twitch', 'welcome_cooldown'))
        except ValueError:
            self.welcome_cooldown = 60

    def make_config_file(self):
        # Create a ConfigParser object
        make_config = self.configparser

        # Add the structure to the file we will create
        make_config.add_section('Twitch')
        make_config.set('Twitch', 'token', '')
        make_config.set('Twitch', 'prefix', '')
        make_config.set('Twitch', 'initial_channels', '')
        make_config.set('Twitch', 'welcome_cooldown', '')
        # Write the new structure to the new file
        with open(r"config.ini", 'w') as configfile:
            make_config.write(configfile)

    def write_config_file(self):
        # Create a ConfigParser object
        write_config = self.configparser

        # Add the structure to the file we will create
        token = input("Please input Twitch Token:")
        write_config.set('Twitch', 'token', token)

        prefix = input("Please input Twitch Prefix:")
        write_config.set('Twitch', 'prefix', prefix)

        channel = input("Please input which channel you want the bot in:")
        write_config.set('Twitch', 'initial_channels', channel)

        cooldown = input("Please input your wished cooldown on welcome:")
        write_config.set('Twitch', 'welcome_cooldown', cooldown)

        # Write the new structure to the new file
        with open(r"config.ini", 'w') as configfile:
            write_config.write(configfile)
