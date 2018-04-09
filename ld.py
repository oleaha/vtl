from simulation.camera.lane import LaneDetection
import Queue
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(relativeCreated)6d %(threadName)s - %(funcName)21s():%(lineno)s ] : %(message)s')


q = Queue.LifoQueue()
l = LaneDetection(q)

for i in range(0, 30):
    logging.debug("Queue: " + str(q.get()))
    time.sleep(1)

logging.debug("Stopping LD")
l.stop_ld(False)

for i in range(0, 10):
    logging.debug("Sleeping...")
    time.sleep(1)



