import asyncio
from dotenv import load_dotenv
load_dotenv()

from metrics import run_metrics

if __name__ == '__main__':
    asyncio.run(run_metrics())