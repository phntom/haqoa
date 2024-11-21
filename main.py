import logging
from os import chdir
from tempfile import TemporaryDirectory

from haqoa.logs import logging_setup

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    logging_setup(logger)

    with TemporaryDirectory() as tmpdir:
        logging.info("Changing directory to %s", tmpdir)
        chdir(tmpdir)
        from haqoa import alert
        alert.run()
