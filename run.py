# coding=utf-8

import logging
import sys
import system.config as config
import system.util as util

from twisted.internet import reactor
from system.core import CoreFactory

logging.basicConfig(format="%(asctime)s | %(name)8s | %(levelname)8s | %(message)s", datefmt="%d %b %Y - %H:%M:%S",
                    level=(logging.DEBUG if "--debug" in sys.argv else logging.INFO))

logger = logging.getLogger("Init")
logger.info("Starting up...")

conf = config.conf()
networking = conf.get("networking")
if not networking:
    logger.critical("Networking configuration is unavailable. The program will now terminate.")
    exit(1)

factory = CoreFactory()

try:
    reactor.listenTCP(networking["port"], factory)

    logger.info("Now listening on port %s." % networking["port"])

    reactor.run()
except Exception as e:
    logger.error("Error starting up: %s" % e)
    util.output_exception(logger)
finally:
    try:
        logger.info("Shutting down..")
        factory.cleanup()
    except:
        pass
