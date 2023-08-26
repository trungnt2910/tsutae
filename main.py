from client import Client
import json

from config import Config

def main():
    config: Config
    with open("config.json", "rb") as fin:
        config_json = json.load(fin)
        config = Config(
            config_json["token"],
            config_json["channels"],
            config_json["history_age"],
            config_json["history_limit"]
        )
    client = Client(config)
    client.run()

if __name__ == "__main__":
    main()
