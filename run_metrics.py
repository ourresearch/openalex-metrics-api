import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

from metrics import run_metrics

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run OpenAlex metrics comparison')
    parser.add_argument('--test', action='store_true', help='Run in test mode (skip saving to database)')
    
    args = parser.parse_args()
    
    asyncio.run(run_metrics(test=args.test))