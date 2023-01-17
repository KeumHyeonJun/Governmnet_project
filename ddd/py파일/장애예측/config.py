import configparser

config = configparser.ConfigParser()
config.read('config.ini')

host = config["impala"]["host"]
port = int(config["impala"]["port"])
user = config["impala"]["user"]
password = config["impala"]["password"]