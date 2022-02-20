import logging

class EventLogs:
    def logSending(self, receiverName, content):
        logging.info(f"SENDING ITEM TO =====: {receiverName}")
        logging.info(f"======== WITH CONTENT: {content}")

    def logReceiving(self, senderName, content):
        logging.info(f"RECEIVE ITEM FROM====: {senderName}")
        logging.info(f"======== WITH CONTENT: {content}")




