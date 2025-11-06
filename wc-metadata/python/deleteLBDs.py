"""
Script to delete LBD (Linked Bibliographic Data) records for OCLC numbers from a spreadsheet.

This script reads a spreadsheet containing OCLC numbers, searches for LBD records
associated with each OCLC number, and deletes them.

Usage:
    python deleteLBDs.py input_file.csv
    python deleteLBDs.py input_file.csv --output output_file.csv
    python deleteLBDs.py input_file.csv --column oclcNumber

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
        A tuple containing the LBD control number and status
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
    
    return control_number, status


def delete_lbd(lbd_control_number):
    """
    Delete an LBD record using its control number.
    
    Args:
        lbd_control_number: The LBD control number to delete
        
    Returns:
        Status string indicating success or failure
    """
    if not lbd_control_number:
        return 'skipped_no_control_number'
    
    request_url = f"https://metadata.api.oclc.org/worldcat/manage/lbds/{lbd_control_number}"
    try:
        r = oauth_session.delete(request_url, headers={"Accept": "application/json"})
        r.raise_for_status()
        status = 'success'
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            status = 'not_found'
        else:
            status = f'http_error_{err.response.status_code}'
    except Exception as e:
        status = f'error_{str(e)}'
    
    return status


def process_oclc_number(oclc_number):
    """
    Process a single OCLC number: look up LBD control number and delete it.
    
    Args:
        oclc_number: The OCLC number to process
        
    Returns:
        A pandas Series containing the LBD control number, lookup status, and deletion status
    """
    # Look up LBD control number
    control_number, lookup_status = get_lbd_control_number(str(oclc_number))
    
    # Delete LBD if control number was found
    if lookup_status == 'success' and control_number:
        deletion_status = delete_lbd(control_number)
    else:
        deletion_status = 'skipped'
    
    return pd.Series([control_number, lookup_status, deletion_status])


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Delete LBD records for OCLC numbers from a spreadsheet.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deleteLBDs.py input.csv
  python deleteLBDs.py input.csv --output results.csv
  python deleteLBDs.py input.csv --column oclcNumber
  python deleteLBDs.py input.csv --output results.csv --column oclcNumber
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
        help='Output CSV file name (default: input_file_lbd_deleted.csv)'
    )
    parser.add_argument(
        '--column', '-c',
        type=str,
        default=None,
        help='Column name containing OCLC numbers (default: auto-detect)'
    )
    return parser.parse_args()


def main():
    """Main function to process spreadsheet and delete LBD records."""
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
        print("See example.env for required variables.")
        sys.exit(1)
    
    # Set up OAuth authentication
    # Scope needed for viewing and managing LBDs
    scope = ['WorldCatMetadataAPI:view_my_local_bib_data', 'WorldCatMetadataAPI:manage_institution_lbds']
    
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
    print(f"Attempting to obtain OAuth token from: {token_url}")
    print(f"Using scope: {scope}")
    try:
        token = oauth_session.fetch_token(
            token_url=token_url,
            auth=auth
        )
        print("Successfully obtained OAuth token")
        if token:
            print(f"Token type: {token.get('token_type', 'N/A')}")
            print(f"Token expires in: {token.get('expires_in', 'N/A')} seconds")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error obtaining OAuth token: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response body: {e.response.text}")
        if hasattr(e.response, 'status_code'):
            print(f"Status code: {e.response.status_code}")
        sys.exit(1)
    except Exception as e:
        print(f"Error obtaining OAuth token: {e}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Response body: {e.response.text}")
        sys.exit(1)
    
    # Process each OCLC number: look up LBD and delete it
    print("\nProcessing records...")
    csv_read[['lbdControlNumber', 'lookupStatus', 'deletionStatus']] = csv_read.apply(
        lambda row: process_oclc_number(row[oclc_column]),
        axis=1
    )
    
    # Generate output filename if not specified
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_lbd_deleted.csv"
    
    # Write results to output file
    try:
        csv_read.to_csv(output_file, index=False)
        print(f"\nResults written to '{output_file}'")
        print(f"Total records processed: {len(csv_read)}")
        
        # Print summary statistics
        successful_lookups = len(csv_read[csv_read['lookupStatus'] == 'success'])
        successful_deletions = len(csv_read[csv_read['deletionStatus'] == 'success'])
        multiple_lbds = len(csv_read[csv_read['lookupStatus'] == 'multiple_lbds_found'])
        no_lbd_found = len(csv_read[csv_read['lookupStatus'] == 'no_lbd_found'])
        
        print(f"\nSummary:")
        print(f"  Successful lookups: {successful_lookups}")
        print(f"  Successful deletions: {successful_deletions}")
        print(f"  Records with multiple LBDs: {multiple_lbds}")
        print(f"  Records with no LBD found: {no_lbd_found}")
        print(f"  Records skipped: {len(csv_read[csv_read['deletionStatus'] == 'skipped'])}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

