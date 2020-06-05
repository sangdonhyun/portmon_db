import time
import example
import os
while True:
    #example.PortInfo().main()
    try:
        os.popen('python example.py')
    except:
        pass
    time.sleep(600)