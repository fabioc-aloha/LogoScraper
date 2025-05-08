"""Test script to generate logos for specific TPIDs"""

import os
import sys
from pathlib import Path
# Add project root to sys.path for module imports
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)
import pandas as pd
from services.input_data_service import InputDataService
from utils.company_processor import CompanyProcessor

def test_specific_logos():
    # Specific TPIDs we want to test
    target_tpids = ['54491231', '1112118']  # Korean and Turkish
    
    # Setup output directories
    output_folder = os.path.join('temp', 'test_logos')
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Testing logo generation for TPIDs: {', '.join(target_tpids)}")
    print(f"Output folder: {output_folder}")
    
    # Get input data
    try:
        service = InputDataService()
        df = service.get_data()
        filtered_df = df[df['tpid'].astype(str).isin(target_tpids)]
        
        if len(filtered_df) == 0:
            print("No matching companies found!")
            return
        
        print(f"Found {len(filtered_df)} companies to process:")
        for _, row in filtered_df.iterrows():
            print(f"- TPID: {row['tpid']}, Name: {row['crmaccountname']}")
        
        # Process each company
        processor = CompanyProcessor(output_folder, 'temp')
        
        for _, row in filtered_df.iterrows():
            print(f"\nProcessing company: {row['crmaccountname']} (TPID: {row['tpid']})")
            success, source, data = processor.process_company(row)
            status = "SUCCESS" if success else "FAILED"
            print(f"Result: {status} - Source: {source}")
            print(f"Logo saved to: {os.path.join(output_folder, str(row['tpid']) + '.png')}")
            
        print("\nLogo generation test complete!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
if __name__ == "__main__":
    test_specific_logos()