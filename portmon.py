
import time
import os

class portMon():
    def __init__(self):
        pass

    def main(self):
        try:
            os.popen('portmon.bat').read()
        except:
            pass


if __name__=='__main__':
    while True:
        portMon().main()
        time.sleep(600)