from openpyxl import load_workbook
import xlrd
import os

def verify_conversion(xlsx_path, xls_path):
    """
    Compare .xlsx and .xls files to ensure data integrity
    """
    print(f"\nVerifying: {os.path.basename(xlsx_path)} vs {os.path.basename(xls_path)}")
    print("="*70)
    
    issues = []
    
    try:
        # Load both files
        wb_xlsx = load_workbook(xlsx_path, data_only=True)
        wb_xls = xlrd.open_workbook(xls_path)
        
        # Check sheet count
        xlsx_sheets = wb_xlsx.sheetnames
        xls_sheets = wb_xls.sheet_names()
        
        if len(xlsx_sheets) != len(xls_sheets):
            issues.append(f"Sheet count mismatch: {len(xlsx_sheets)} vs {len(xls_sheets)}")
        
        # Compare each sheet
        for sheet_name in xlsx_sheets:
            if sheet_name not in xls_sheets:
                issues.append(f"Sheet '{sheet_name}' missing in .xls")
                continue
            
            ws_xlsx = wb_xlsx[sheet_name]
            ws_xls = wb_xls.sheet_by_name(sheet_name)
            
            # Get dimensions
            xlsx_rows = ws_xlsx.max_row
            xlsx_cols = ws_xlsx.max_column
            xls_rows = ws_xls.nrows
            xls_cols = ws_xls.ncols
            
            print(f"\nSheet: {sheet_name}")
            print(f"  .xlsx: {xlsx_rows} rows × {xlsx_cols} cols")
            print(f"  .xls:  {xls_rows} rows × {xls_cols} cols")
            
            if xlsx_rows != xls_rows or xlsx_cols != xls_cols:
                issues.append(f"Sheet '{sheet_name}': dimension mismatch")
            
            # Sample check: compare first 10 rows of data
            mismatches = 0
            max_check_rows = min(10, xlsx_rows, xls_rows)
            
            for row_idx in range(max_check_rows):
                for col_idx in range(min(xlsx_cols, xls_cols)):
                    xlsx_val = ws_xlsx.cell(row_idx + 1, col_idx + 1).value
                    xls_val = ws_xls.cell_value(row_idx, col_idx)
                    
                    # Normalize None/"" differences
                    xlsx_val = "" if xlsx_val is None else str(xlsx_val)
                    xls_val = "" if xls_val == "" else str(xls_val)
                    
                    if xlsx_val != xls_val:
                        mismatches += 1
                        if mismatches <= 3:  # Show first 3 mismatches
                            print(f"  ⚠ Mismatch at [{row_idx+1},{col_idx+1}]: '{xlsx_val}' vs '{xls_val}'")
            
            if mismatches > 0:
                issues.append(f"Sheet '{sheet_name}': {mismatches} data mismatches in first 10 rows")
        
        # Summary
        print("\n" + "="*70)
        if not issues:
            print("✓ PASSED: Files match!")
        else:
            print("✗ ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"✗ ERROR during verification: {str(e)}")
        return False

# Verify all conversions
def verify_all(input_folder, output_folder):
    import glob
    xlsx_files = glob.glob(os.path.join(input_folder, "*.xlsx"))
    
    results = []
    for xlsx_file in xlsx_files:
        filename = os.path.basename(xlsx_file)
        xls_filename = filename.replace('.xlsx', '.xls')
        xls_path = os.path.join(output_folder, xls_filename)
        
        if os.path.exists(xls_path):
            passed = verify_conversion(xlsx_file, xls_path)
            results.append((filename, passed))
        else:
            print(f"✗ Missing converted file: {xls_filename}")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    for filename, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {filename}")

# Usage
input_folder = "."
output_folder = "./converted"

verify_all(input_folder, output_folder)
