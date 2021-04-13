from gsheet_service import settings
from gsheet_service.types import Result, config, get_provider_sheet
import rpyc
import json
import asyncio


class RPCService:
    def __init__(self, host, port, server_method):
        self.SCHEDULER_URL = host
        self.SCHEDULER_PORT = port
        self.server_method = server_method

    @property
    def rpc_connection(self):
        return rpyc.connect(self.SCHEDULER_URL, int(self.SCHEDULER_PORT))

    async def rpc_create_job(self, trigger="interval", args=None, **kwargs):
        # job = conn.root.add_job('server:print_text', args=['Hello, John'])
        job = self.rpc_connection.root.add_job(
            self.server_method,
            trigger=trigger,
            args=args,
            **kwargs
            # # trigger="interval",  # interval date or cron
            # args=["https://payment.careerlyft.com", "GET"],
            # # minutes=1,  # **trigger_args
            # # minutes=1,  # **trigger_args
        )
        return job.id

    async def rpc_pause_job(self, job_id=None):
        if job_id:
            # exists = await self.rpc_check_job_existence(job_id)
            # if exists:
            self.rpc_connection.root.pause_job(job_id)

    async def rpc_resume_job(self, job_id=None):
        if job_id:
            # exists = await self.rpc_check_job_existence(job_id)
            # if exists:
            self.rpc_connection.root.resume_job(job_id)

    async def rpc_delete_job(self, job_id=None):
        if job_id:
            # exists = await self.rpc_check_job_existence(job_id)
            # if exists:
            self.rpc_connection.root.remove_job(job_id)

    def get_jobs(self, job_id=None):
        jobs = self.rpc_connection.root.get_jobs()
        return jobs

    def parse_jobs(self, job_id=None):
        jobs = self.rpc_connection.root.parse_jobs()
        jobs = json.loads(jobs)
        if job_id:
            return [x for x in jobs if x["id"] == job_id]
        return jobs


async def create_job(identifier, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    single_job = data.pop("job", None)
    multiple_jobs = data.pop("jobs", [])
    endpoint = data.pop("endpoint", None)
    method = data.pop("method", None)
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config and all([endpoint, method, any([single_job, multiple_jobs])]):
        instance = RPCService(config["host"], config["port"], config["server_method"])
        if multiple_jobs:
            job_ids = await asyncio.gather(
                *[
                    instance.rpc_create_job(
                        args=[endpoint, method, json.dumps(x)],
                        **data,
                    )
                    for x in multiple_jobs
                ]
            )
        else:
            job_id = await instance.rpc_create_job(
                args=[endpoint, method, json.dumps(single_job)], **data
            )
            job_ids = [job_id]
        return Result(data=job_ids)
    return Result(
        error="Error scheduling job, missing field, job, jobs,endpoint,method,"
    )


async def pause_job(identifier, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    single_job = data.pop("job_id", None)
    multiple_jobs = data.pop("job_ids", [])
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config and any([single_job, multiple_jobs]):
        instance = RPCService(config["host"], config["port"], config["server_method"])
        if multiple_jobs:
            await asyncio.gather(
                *[instance.rpc_pause_job(job_id=x) for x in multiple_jobs]
            )
        else:
            await instance.rpc_pause_job(job_id=single_job)
        return Result(
            data={
                "status": "successful",
                "job_id": single_job,
                "job_ids": multiple_jobs,
            }
        )
    return Result(error="Invalid parameter passed, job_id, job_ids")


async def resume_job(identifier, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    single_job = data.pop("job_id", None)
    multiple_jobs = data.pop("job_ids", [])
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config and any([single_job, multiple_jobs]):
        instance = RPCService(config["host"], config["port"], config["server_method"])
        if multiple_jobs:
            await asyncio.gather(
                *[instance.rpc_resume_job(job_id=x) for x in multiple_jobs]
            )
        else:
            await instance.rpc_resume_job(job_id=single_job)
        return Result(
            data={
                "status": "successful",
                "job_id": single_job,
                "job_ids": multiple_jobs,
            }
        )
    return Result(error="Invalid parameter passed, job_id, job_ids")


async def delete_job(identifier, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    single_job = data.pop("job_id", None)
    multiple_jobs = data.pop("job_ids", [])
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config and any([single_job, multiple_jobs]):
        instance = RPCService(config["host"], config["port"], config["server_method"])
        if multiple_jobs:
            await asyncio.gather(
                *[instance.rpc_delete_job(job_id=x) for x in multiple_jobs]
            )
        else:
            await instance.rpc_delete_job(job_id=single_job)
        return Result(
            data={
                "status": "successful",
                "job_id": single_job,
                "job_ids": multiple_jobs,
            }
        )
    return Result(error="Invalid parameter passed, job_id, job_ids")


async def get_all_jobs(identifier, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    status = data.get("status", "all")
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config:
        instance = RPCService(config["host"], config["port"], config["server_method"])
        jobs = instance.parse_jobs()
        if status == "paused":
            jobs = [x for x in jobs if x["next_run_time"] == ""]
        if status == "running":
            jobs = [x for x in jobs if x["next_run_time"] != ""]

        return Result(data=jobs)
    return Result(error="Error with passed parameters")


async def get_job(identifier, job_id, **data) -> Result:
    link = data.pop("link", None) or settings.SCHEDULER_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.SCHEDULER_SHEET_NAME
    config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if config:
        instance = RPCService(config["host"], config["port"], config["server_method"])
        jobs = instance.parse_jobs(job_id)
        if jobs:
            return Result(data=jobs[0])
    return Result(error=f"Could not fetch info for job with id {job_id}")