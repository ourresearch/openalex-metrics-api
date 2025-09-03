#!/usr/bin/env python3

import json
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from models import Sample


def load_samples(selected_sample_name=None):
    """Load all samples from samples.json into the database."""
    
    # Get the path to samples.json (assuming it's in the same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    samples_file = os.path.join(script_dir, 'samples.json')
    
    if not os.path.exists(samples_file):
        print(f"Error: {samples_file} not found!")
        return
    
    # Load the JSON data
    print(f"Loading samples from {samples_file}...")
    with open(samples_file, 'r') as f:
        samples_data = json.load(f)
    
    # Create application context
    with app.app_context():
        samples_loaded = 0
        for sample_key, sample_data in samples_data.items():
            if selected_sample_name and sample_data.get('name', sample_key) != selected_sample_name:
                continue
            try:
                # Parse the date string
                date_str = sample_data.get('date', '')
                try:
                    # Try to parse the date (assuming format like "2025-07-21")
                    date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                except ValueError:
                    # If date parsing fails, use current date
                    print(f"Warning: Could not parse date '{date_str}' for sample '{sample_key}', using current date")
                    date_obj = datetime.now()
                
                # Create the Sample object
                sample = Sample(
                    name=sample_data.get('name', sample_key),  # Use key as fallback name
                    entity=sample_data.get('entity', None),
                    type=sample_data.get('type', None),
                    description=sample_data.get('description', ''),
                    date=date_obj,
                    ids=sample_data.get('ids', [])  # JSON array will be stored as JSON
                )
                
                # Check if a sample with this name already exists
                sample_name = sample_data.get('name', sample_key)
                existing_sample = Sample.query.filter_by(name=sample_name).first()
                
                if existing_sample:
                    # Update existing sample
                    existing_sample.entity = sample_data.get('entity', None)
                    existing_sample.type = sample_data.get('type', None)
                    existing_sample.description = sample_data.get('description', '')
                    existing_sample.date = date_obj
                    existing_sample.ids = sample_data.get('ids', [])
                    print(f"Updated existing sample: {sample_name}")
                else:
                    # Add new sample to session
                    db.session.add(sample)
                    print(f"Added new sample: {sample_name}")
                
                samples_loaded += 1
            except Exception as e:
                print(f"Error loading sample '{sample_key}': {e}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\nSuccessfully loaded {samples_loaded} samples into the database!")
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load samples into the database.")
    parser.add_argument('--sample', type=str, help="Only load the sample with this name field.")
    args = parser.parse_args()

    load_samples(selected_sample_name=args.sample)