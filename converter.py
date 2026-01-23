from openpyxl import load_workbook
import xlwt
import os
from pathlib import Path

class InvalidFileFormatError(Exception):
    pass

class ConversionError(Exception):
    pass

class FileSizeLimitError(Exception):
    pass

class XLSXConverter:
    def __init__(self, xls_max_rows=65536, xls_max_cols=256):
        self.xls_max_rows = xls_max_rows
        self.xls_max_cols = xls_max_cols
        self._style_cache = {}

    def _get_xlwt_style(self, number_format):
        """Get or create xlwt style for a given number format."""
        if number_format in self._style_cache:
            return self._style_cache[number_format]

        style = xlwt.XFStyle()
        if number_format and number_format != 'General':
            style.num_format_str = number_format

        self._style_cache[number_format] = style
        return style

    def validate_xlsx(self, file_path):
        if not os.path.exists(file_path):
            raise InvalidFileFormatError("File does not exist")

        if not file_path.lower().endswith('.xlsx'):
            raise InvalidFileFormatError("File must have .xlsx extension")

        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)

            for sheet in wb.worksheets:
                if sheet.max_row > self.xls_max_rows:
                    raise FileSizeLimitError(
                        f"Sheet '{sheet.title}' has {sheet.max_row} rows, "
                        f"exceeding XLS format limit of {self.xls_max_rows} rows"
                    )
                if sheet.max_column > self.xls_max_cols:
                    raise FileSizeLimitError(
                        f"Sheet '{sheet.title}' has {sheet.max_column} columns, "
                        f"exceeding XLS format limit of {self.xls_max_cols} columns"
                    )

            wb.close()
            return True
        except FileSizeLimitError:
            raise
        except Exception as e:
            raise InvalidFileFormatError(f"Invalid XLSX file: {str(e)}")

    def convert_file(self, input_path, output_path):
        try:
            self.validate_xlsx(input_path)

            # Clear style cache for each conversion
            self._style_cache = {}

            wb_xlsx = load_workbook(input_path, data_only=True)
            wb_xls = xlwt.Workbook()

            for sheet_name in wb_xlsx.sheetnames:
                ws_xlsx = wb_xlsx[sheet_name]

                truncated_name = sheet_name[:31]
                ws_xls = wb_xls.add_sheet(truncated_name)

                # Iterate over cells (not values_only) to get formatting
                for row_idx, row in enumerate(ws_xlsx.iter_rows()):
                    for col_idx, cell in enumerate(row):
                        if cell.value is not None:
                            try:
                                # Get the number format and create style
                                style = self._get_xlwt_style(cell.number_format)
                                ws_xls.write(row_idx, col_idx, cell.value, style)
                            except Exception:
                                # Fallback: write as string without style
                                ws_xls.write(row_idx, col_idx, str(cell.value))

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            wb_xls.save(output_path)

            return True
        except (InvalidFileFormatError, FileSizeLimitError):
            raise
        except Exception as e:
            raise ConversionError(f"Conversion failed: {str(e)}")
