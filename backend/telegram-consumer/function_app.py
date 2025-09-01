import asyncio
import logging

import azure.functions as func
from consumer import main

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def FetchTelegramData(myTimer: func.TimerRequest) -> None:

    if myTimer.past_due:
        logging.info("The timer is past due!")

    asyncio.run(main())
    logging.info("Python timer trigger function executed.")
