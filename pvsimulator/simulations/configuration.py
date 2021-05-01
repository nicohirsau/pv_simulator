import configparser

CONFIGURATION = {
    'host': 'localhost',
    'username': 'guest',
    'password': 'guest',
    'queue_name': 'pv_simulation'
}

def read_config_file(filepath):
    config_parser = configparser.RawConfigParser()
    if len(config_parser.read([filepath])) is 0:
        print("Could not find config file at location", filepath)
        return

    global CONFIGURATION
    for config_name in list(CONFIGURATION):
        try:
            read_value = config_parser.get(
                'simulation-config', 
                config_name
            )
            CONFIGURATION[config_name] = read_value
        except configparser.NoSectionError as e:
            print(
                "Could not find section 'simulation-config'",
                "in the config file '" + filepath + "'!"
            )
            print(
                "Leaving values at default."
            )
            return
        except configparser.NoOptionError as e:
            print(
                "Could not find option '" + config_name + "'",
                "in the config file '" + filepath + "'"
            )
            print("Leaving it at default.")
    