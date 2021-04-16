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
from apscheduler.triggers.combining import AndTrigger, OrTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
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
        logging.info({**params, "method": method})
    except TypeError:
        if params:
            params = json.loads(params)
        else:
            params = {}
        if method.upper() == "POST":
            func_params["json"] = params
        else:
            func_params["params"] = params
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
        # add ability to extend triggers
        return scheduler.add_job(func, *args, **kwargs)

    def exposed_add_job_advanced(self, func, **kwargs):
        """
        {
            "operator": "and",
            "values":[
                {
                    "type":"cron",
                    "params":{ "day_of_week": "mon,tue", "hour": 10 }
                },
                {
                    "type":"interval",
                    "params": {"seconds": 60}
                }
            ]
        }
        """
        trigger = kwargs.pop("trigger", None)
        options = {
            "cron": CronTrigger,
            "interval": IntervalTrigger,
            "date": DateTrigger,
        }
        condition = {"and": AndTrigger, "or": OrTrigger}
        trigger = json.loads(trigger)
        if trigger and trigger.get("operator") and trigger.get("values"):
            condition_func = condition[trigger["operator"]]
            get_func = lambda x: options[x["type"]]
            result = condition_func(
                [get_func(x)(**x["params"]) for x in trigger["values"]]
            )
            return scheduler.add_job(func, result, **kwargs)
        # return scheduler.add_job(func, *args, **kwargs)

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

    def exposed_modify_job(self, job_id, jobstore=None, params=None):
        job = scheduler.get_job(job_id)
        if params:
            kwargs = json.loads(params)
            reschedule = kwargs.pop('reschedule',None)
            job.modify(**kwargs)
            if reschedule:
                job.reschedule(**reschedule)
            logging.info("Job modified")

    def exposed_get_job(self, job_id):
        return scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)

    def exposed_get_jobs_ids(self, jobstore=None):
        result = scheduler.get_jobs(jobstore)
        return json.dumps([x.id for x in result])

    def exposed_parse_jobs(self, jobstore=None):
        result = scheduler.get_jobs(jobstore)
        return json.dumps([self.parse_job_info(x) for x in result])

    def parse_job_info(self, job):
        next_run_time = job.next_run_time
        return {
            "kwargs": job.kwargs,
            "args": list(job.args),
            "id": job.id,
            "next_run_time": next_run_time.isoformat() if next_run_time else "",
            "pending": job.pending,
            "max_instances": job.max_instances,
            "coalesce": job.coalesce,
            "triggers": self.parse_trigger_info(job.trigger),
        }

    def parse_trigger_info(self, trigger):
        if hasattr(trigger, "triggers"):
            result = []
            for i in trigger.triggers:
                if isinstance(i, IntervalTrigger):
                    result.append(interval_trigger(i))
                if isinstance(i, CronTrigger):
                    result.append(cron_trigger(i))
                if isinstance(i, DateTrigger):
                    result.append(date_trigger(i))
            return result
        if isinstance(trigger, IntervalTrigger):
            return interval_trigger(trigger)
        if isinstance(trigger, CronTrigger):
            return cron_trigger(trigger)
        if isinstance(trigger, DateTrigger):
            return date_trigger(trigger)
        return {}


def interval_trigger(trigger):
    end_date = trigger.end_date
    start_date = trigger.start_date
    return {
        "start_date": start_date.isoformat() if start_date else "",
        "end_date": end_date.isoformat() if end_date else "",
        "interval": str(trigger.interval),
        "timezone": str(trigger.timezone),
    }


def cron_trigger(trigger: CronTrigger):

    start_date = eval_none(trigger, "start_date")
    end_date = eval_none(trigger, "end_date")
    hour = eval_none(trigger, "hour")
    minute = eval_none(trigger, "minute")
    second = eval_none(trigger, "second")
    year = eval_none(trigger, "year")
    month = eval_none(trigger, "month")
    day = eval_none(trigger, "day")
    week = eval_none(trigger, "week")
    day_of_week = eval_none(trigger, "day_of_week")
    return {
        "start_date": start_date.isoformat() if start_date else "",
        "end_date": end_date.isoformat() if end_date else "",
        "timezone": str(trigger.timezone),
        "cron": " ".join([str(x) for x in trigger.fields]),
    }


def eval_none(trigger, key):
    u = None
    if hasattr(trigger, key):
        u = getattr(trigger, key)
    return u


def date_trigger(trigger):
    start_date = eval_none(trigger, "start_date")
    end_date = eval_none(trigger, "end_date")
    run_date = eval_none(trigger, "run_date")
    return {
        "run_date": run_date.isoformat() if run_date else "",
        "start_date": start_date.isoformat() if start_date else "",
        "end_date": end_date.isoformat() if end_date else "",
    }


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
