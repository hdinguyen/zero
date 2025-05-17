from configparser import ConfigParser, ExtendedInterpolation
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(current_dir, "config.ini")

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(config_path)