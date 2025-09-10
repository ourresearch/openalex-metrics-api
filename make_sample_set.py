import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

from make_sample import make_sample
from schema import last_week_samples_schema

async def build_last_week_samples(test=False):
    """Build all last week samples in parallel"""
    tasks = []
    for entity in last_week_samples_schema.keys():
        for type_ in last_week_samples_schema[entity].keys():
            sample_name = f"{entity.replace('-', ' ').title().replace(' ', '')}{type_.title()}Weekly"
            sample_type = type_
            sample_size = last_week_samples_schema[entity][type_]
            task = make_sample(sample_name, entity, sample_size, sample_type, sample_scope="last-week", test=test)
            tasks.append(task)
    
    # Run all sample creation tasks in parallel
    await asyncio.gather(*tasks)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a set of samples')
    parser.add_argument('--last-week', action='store_true', help='Build last week samples')
    parser.add_argument('--test', action='store_true', help='Run in test mode (skip saving to database)')
    
    args = parser.parse_args()
    
    if args.last_week:
        asyncio.run(build_last_week_samples(test=args.test))
    else:
        print("Please specify a sample set to build")