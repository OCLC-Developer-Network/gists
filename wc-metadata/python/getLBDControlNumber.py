"""
Script to look up LBD control numbers for OCLC numbers from a spreadsheet.

This script reads a spreadsheet containing OCLC numbers, searches for LBD records
associated with each OCLC number, and writes the LBD control numbers to an output file.

Usage:
    python getLBDControlNumber.py input_file.csv
    python getLBDControlNumber.py input_file.csv --output output_file.csv
    python getLBDControlNumber.py input_file.csv --column oclcNumber

Requirements:
    - .env file with API credentials (OCLC_KEY, OCLC_SECRET, OCLC_TOKEN_URL)
    - Input CSV file with OCLC numbers
    - Column in CSV containing OCLC numbers
"""

import pandas as pd
import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_lbd_control_number(oclc_number):
    """
    Search for LBD control number using OCLC number.
    
    Args:
        oclc_number: The OCLC number to search for
        
    Returns:
        A pandas Series containing the LBD control number and status
    """
    # Construct search query using oc: prefix for OCLC number search
    search_query = f"q=oc:{oclc_number}"
    request_url = f"https://metadata.api.oclc.org/worldcat/search/lbds?{search_query}&limit=1"
    
    try:
        r = oauth_session.get(request_url, headers={"Accept": "application/json"})
        r.raise_for_status()
        try:
            result = r.json()
            # Check the total number of LBDs found
            number_of_lbds = result.get('numberOfRecords', 0)
            
            # If more than one LBD is found, return empty control number with special status
            if number_of_lbds > 1:
                control_number = ''
                status = 'multiple_lbds_found'
            elif number_of_lbds == 1:
                # Extract control number from the single LBD record
                local_bib_data = result.get('localBibData', [])
                if local_bib_data:
                    # Control number is in the 'controlNumber' field
                    control_number = local_bib_data[0].get('controlNumber', '')
                    status = 'success'
                else:
                    control_number = ''
                    status = 'no_lbd_found'
            else:
                control_number = ''
                status = 'no_lbd_found'
        except json.decoder.JSONDecodeError:
            control_number = ''
            status = 'json_decode_error'
    except requests.exceptions.HTTPError as err:
        control_number = ''
        status = f'http_error_{err.response.status_code}'
    
    return pd.Series([control_number, status])


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Look up LBD control numbers for OCLC numbers from a spreadsheet.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python getLBDControlNumber.py input.csv
  python getLBDControlNumber.py input.csv --output results.csv
  python getLBDControlNumber.py input.csv --column oclcNumber
  python getLBDControlNumber.py input.csv --output results.csv --column oclcNumber
        """
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input CSV file containing OCLC numbers'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output CSV file name (default: input_file_lbd_results.csv)'
    )
    parser.add_argument(
        '--column', '-c',
        type=str,
        default=None,
        help='Column name containing OCLC numbers (default: auto-detect)'
    )
    return parser.parse_args()


def main():
    """Main function to process spreadsheet and look up LBD control numbers."""
    global auth, oauth_session
    
    # Parse command-line arguments
    args = parse_arguments()
    
    input_file = args.input_file
    output_file = args.output
    oclc_column = args.column
    
    # Load configuration from environment variables
    oclc_key = os.getenv('OCLC_KEY')
    oclc_secret = os.getenv('OCLC_SECRET')
    token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')
    
    if not oclc_key or not oclc_secret:
        print("Error: OCLC_KEY and OCLC_SECRET environment variables must be set.")
        print("Please create a .env file with your API credentials.")
        print("See .env.example for required variables.")
        sys.exit(1)
    
    # Set up OAuth authentication
    # Scope needed for viewing LBDs
    scope = ['WorldCatMetadataAPI:view_institution_lbds']
    
    auth = HTTPBasicAuth(oclc_key, oclc_secret)
    client = BackendApplicationClient(client_id=oclc_key, scope=scope)
    oauth_session = OAuth2Session(client=client)
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Read input CSV file
    try:
        csv_read = pd.read_csv(input_file, index_col=False, encoding='utf-8')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Determine the column name for OCLC numbers
    if oclc_column:
        # User specified a column name
        if oclc_column not in csv_read.columns:
            print(f"Error: Column '{oclc_column}' not found in CSV file.")
            print(f"Available columns: {', '.join(csv_read.columns)}")
            sys.exit(1)
    else:
        # Auto-detect column name
        for col_name in ['oclcNumber', 'oclc_number', 'OCLC Number', 'OCLCNumber', 'oclc']:
            if col_name in csv_read.columns:
                oclc_column = col_name
                break
        
        # If no common column name found, use the first column
        if oclc_column is None:
            oclc_column = csv_read.columns[0]
            print(f"Warning: Using first column '{oclc_column}' as OCLC number column.")
    
    print(f"Reading OCLC numbers from column '{oclc_column}' in '{input_file}'")
    print(f"Processing {len(csv_read)} records...")
    
    # Fetch OAuth token
    try:
        token = oauth_session.fetch_token(
            token_url=token_url,
            auth=auth
        )
    except Exception as e:
        print(f"Error obtaining OAuth token: {e}")
        sys.exit(1)
    
    # Process each OCLC number and look up LBD control number
    csv_read[['lbdControlNumber', 'status']] = csv_read.apply(
        lambda row: get_lbd_control_number(str(row[oclc_column])),
        axis=1
    )
    
    # Generate output filename if not specified
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_lbd_results.csv"
    
    # Write results to output file
    try:
        csv_read.to_csv(output_file, index=False)
        print(f"\nResults written to '{output_file}'")
        print(f"Total records processed: {len(csv_read)}")
        print(f"Successful lookups: {len(csv_read[csv_read['status'] == 'success'])}")
        print(f"Records with multiple LBDs: {len(csv_read[csv_read['status'] == 'multiple_lbds_found'])}")
        print(f"Records with no LBD found: {len(csv_read[csv_read['status'] == 'no_lbd_found'])}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

