from threading import Thread
from utils.queue_package import QueuePackage
from utils.event_logs import EventLogs
from globals.app_queue import q
from globals.thread_names import *
import logging


# Create Thread that will convert ROI into a cropped image into resources file
class KeyboardEventReceiverThread(Thread, EventLogs):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(KeyboardEventReceiverThread, self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            # Check queues is not empty
            if not q.empty():
                if len(list(q.queue)) > 0:
                    # peek the item in queue
                    item = list(q.queue)[0]

                    # make sure peeked item is the instance of data Package
                    if isinstance(item, QueuePackage):
                        # Check that sender is ObjectDetection RS and the receiver is CropRoi
                        if item.json()["sentFrom"] == OBJECT_DETECTION_RS_THREAD_NAME \
                                and item.json()["sentTo"] == self.getName():
                            # consume data and take it out from queue list
                            consumedItem = q.get().json()
                            senderName = consumedItem["sentFrom"]
                            content = consumedItem["content"]
                            self.logReceiving(senderName, content)

                        # Terminate threads when the main threads send termination package
                        # to all existing threads
                        if item.json()["sentFrom"] == OBJECT_DETECTION_RS_THREAD_NAME \
                                and item.json()["sentTo"] == ALL_THREADS:
                            logging.debug(f"{self.name}: Terminating...")
                            break
