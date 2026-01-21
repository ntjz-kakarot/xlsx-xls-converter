from openpyxl import load_workbook
import xlwt
import os
import glob

def convert_xlsx_to_xls(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    xlsx_files = glob.glob(os.path.join(input_folder, "*.xlsx"))
    
    if not xlsx_files:
        print("No .xlsx files found!")
        return
    
    for xlsx_file in xlsx_files:
        try:
            wb_xlsx = load_workbook(xlsx_file, data_only=True)
            wb_xls = xlwt.Workbook()
            
            for sheet_name in wb_xlsx.sheetnames:
                ws_xlsx = wb_xlsx[sheet_name]
                ws_xls = wb_xls.add_sheet(sheet_name[:31])  # .xls sheet name limit
                
                for row_idx, row in enumerate(ws_xlsx.iter_rows(values_only=True)):
                    for col_idx, value in enumerate(row):
                        if value is not None:
                            ws_xls.write(row_idx, col_idx, value)
            
            filename = os.path.basename(xlsx_file)
            xls_filename = filename.replace('.xlsx', '.xls')
            output_path = os.path.join(output_folder, xls_filename)
            
            wb_xls.save(output_path)
            print(f"✓ Converted: {filename} → {xls_filename}")
            
        except Exception as e:
            print(f"✗ Failed to convert {filename}: {str(e)}")

input_folder = "."
output_folder = "./converted"

convert_xlsx_to_xls(input_folder, output_folder)