import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

from daix_code_agent.new_agent import New_Agent


@activity.defn
def run_activity(request: dict[str, str]) -> dict[str, str]:
    agent = New_Agent([])

    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": request["prompt"]}]
        },
        config={
            "max_concurrency": 1,
            "recursion_limit": 100,
        },
    )

    return result

@workflow.defn
class Agent_Workflow:
    @workflow.run
    async def run(self, request: dict[str, str]) -> dict[str, str]:
        result = await workflow.execute_activity(run_activity, request, start_to_close_timeout=timedelta(minutes=2))
        return {"result": result["messages"][-1].text}


async def main() -> None:
    client = await Client.connect("http://localhost:7233", namespace='default')

    with ThreadPoolExecutor(max_workers=4) as executor:
        worker = Worker(
            client,
            task_queue='daix-agent',
            activity_executor=executor,
            workflows=[Agent_Workflow],
            activities=[run_activity],
            max_concurrent_activities=4
        )
        await  worker.run()

if __name__ == "__main__":
    asyncio.run(main())