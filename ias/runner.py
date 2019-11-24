import subprocess
from os.path import join, realpath, dirname

def run(puppeteer_script_filepath, username, password):
    relpath = lambda filename: join(dirname(realpath(__file__)), filename)

    subprocess.check_call(f"node {relpath('index.js')} --puppeteer_script_filepath={puppeteer_script_filepath} --username={username} --password={password}".split())

