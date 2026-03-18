import pandas as pd
import os
import hashlib
from datetime import datetime
from utils.logger import logger

class FileProcessor:
    def process(self, file_path: str) -> list:
        logger.info(f"Processing file: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in [".xlsx", ".xls"]:
            raise ValueError(f"Unsupported file type: {ext}")
            
        return self._process_excel(file_path)

    def _process_excel(self, file_path: str) -> list:
        file_name = os.path.basename(file_path)
        try:
            # Read all sheets; openpyxl for xlsx
            engine = 'openpyxl' if file_path.endswith('.xlsx') else None
            sheets = pd.read_excel(file_path, sheet_name=None, engine=engine)
        except Exception as e:
            raise ValueError(f"Failed to read excel file: {e}")

        all_records = []
        process_time = datetime.utcnow().isoformat()

        for sheet_name, df in sheets.items():
            # Remove entirely empty rows
            df.dropna(how='all', inplace=True)
            
            if df.empty:
                continue
                
            # Clean column names (lowercase, no spaces, strip whitespace)
            df.columns = [str(col).strip().lower().replace(" ", "_").replace(".", "") for col in df.columns]

            # Replace NaN with None (which becomes null in MongoDB)
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            
            for row in records:
                # Add metadata
                row["source_file"] = file_name
                row["sheet_name"] = sheet_name
                row["processed_timestamp"] = process_time
                
                # Generate a row-level hash for deduplication
                # Hash original row values (excluding metadata)
                row_str = "".join(str(v) for k, v in row.items() if k not in ["source_file", "sheet_name", "processed_timestamp"])
                row["row_hash"] = hashlib.sha256(row_str.encode('utf-8')).hexdigest()
                
                all_records.append(row)

        return all_records