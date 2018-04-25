from simulation.camera.lane_mp import LaneDetectionMP
from multiprocessing import Queue
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(relativeCreated)6d %(threadName)s - %(funcName)21s():%(lineno)s ] : %(message)s')


q = Queue()
l = LaneDetectionMP(q)
l.lane_detection()

#for i in range(0, 30):
#    logging.debug("Queue: " + str(q.get()))
#    time.sleep(1)

#logging.debug("Stopping LD")
#l.stop_ld(False)

#for i in range(0, 10):
#    logging.debug("Sleeping...")
#    time.sleep(1)



