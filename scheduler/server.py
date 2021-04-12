"""
This is an example showing how to make the scheduler into a remotely accessible service.
It uses RPyC to set up a service through which the scheduler can be made to add, modify and remove
jobs.
To run, first install RPyC using pip. Then change the working directory to the ``rpc`` directory
and run it with ``python -m server``.
"""

import rpyc
from rpyc.utils.server import ThreadedServer
import requests
import os
import json
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from utils import init_logging

logging = init_logging(__name__)


def print_text(text):
    print(text)


DATABASE_URL = os.getenv("DATABASE_URL")


def process_api_job(url, method, params=None, **kwargs):
    func = requests.get
    func_params = {**kwargs}
    if method.upper() == "POST":
        func = requests.post
        func_params["json"] = params
    else:
        func_params["params"] = params
    logging.info(params)
    try:
        logging.info({**params,'method':method})
    except TypeError:
        params = json.loads(params)
        if method.upper() == 'POST':
            func_params['json'] = params
        else:
            func_params['params'] = params
    try:
        result = func(url, **func_params)
        if result.status_code >= 400:
            logging.info(result.text)
            logging.info("Error when processing api job")
        else:
            data = result.json()
            logging.info(data)
    except Exception as e:
        logging.error("Url is {}".format(url))
        logging.error(e)


class SchedulerService(rpyc.Service):
    def exposed_add_job(self, func, *args, **kwargs):
        return scheduler.add_job(func, *args, **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(
        self, job_id, jobstore=None, trigger=None, **trigger_args
    ):
        return scheduler.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, jobstore=None):
        return scheduler.pause_job(job_id, jobstore)

    def exposed_resume_job(self, job_id, jobstore=None):
        return scheduler.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, jobstore=None):
        scheduler.remove_job(job_id, jobstore)
        logging.info("Job removed ", job_id)

    def exposed_get_job(self, job_id):
        return scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)


if __name__ == "__main__":
    jobstores = {"default": SQLAlchemyJobStore(url=DATABASE_URL)}
    job_defaults = {"coalesce": False, "max_instances": 3}
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.start()
    protocol_config = {"allow_public_attrs": True}
    server = ThreadedServer(
        SchedulerService, port=12345, protocol_config=protocol_config
    )
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
