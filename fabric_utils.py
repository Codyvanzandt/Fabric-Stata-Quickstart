import os
import struct
import yaml
import warnings
import pandas as pd
import sqlalchemy as sa
from azure.identity import InteractiveBrowserCredential
from deltalake import write_deltalake

warnings.filterwarnings("ignore", message=".*response_mode='form_post' is recommended.*")

_credential = InteractiveBrowserCredential()

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def read_table(schema: str, table_name: str) -> pd.DataFrame:
    """Reads from the Warehouse using the SQL engine."""
    config = load_config()
    server = config['fabric']['warehouse_server']
    db = config['fabric']['warehouse_name']
    
    # 1. Pop open browser for Microsoft Login (Database Scope)
    token_bytes = _credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    # 2. Connect via ODBC
    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={db};Encrypt=yes;"
    engine = sa.create_engine(
        f"mssql+pyodbc:///?odbc_connect={conn_str}", 
        connect_args={'attrs_before': {1256: token_struct}}
    )
    
    # 3. Download data
    safe_query = f"SELECT * FROM {schema}.{table_name}"
    df = pd.read_sql(safe_query, engine)

    return df

def write_table(df: pd.DataFrame, schema: str, table_name: str):
    """
    Writes directly to the Fabric Lakehouse using pure Delta Lake files,
    incorporating the schema into the OneLake path.
    """
    config = load_config()
    lakehouse_path = config['fabric']['lakehouse_abfs_path']
    
    # Inject /Tables/ so Fabric recognizes it as a managed Delta table.
    # We concatenate schema and table_name since standard Lakehouses flatten schemas.
    full_table_path = f"{lakehouse_path}/Tables/{schema}_{table_name}"
    
    # 1. Get token for Storage
    token = _credential.get_token("https://storage.azure.com/.default").token
    
    # 2. Write directly to OneLake
    storage_options = {
        "bearer_token": token,
        "use_fabric_endpoint": "true"
    }
    
    write_deltalake(full_table_path, df, mode="overwrite", storage_options=storage_options)

def run_stata_script(df: pd.DataFrame, do_file_path: str) -> pd.DataFrame:
    """
    Invisibly passes a Pandas DataFrame into Stata, runs a native .do file, 
    and returns the resulting dataset back as a Pandas DataFrame.
    """
    # Import inside the function so it doesn't crash on machines without Stata
    from pystata import stata 
    
    # Let Python figure out the absolute path so Stata doesn't get lost
    absolute_path = os.path.abspath(do_file_path)
    
    # Push data in
    stata.pdataframe_to_data(df, force=True)
    
    # Run their native code (Wrap the path in double quotes to protect against spaces)
    stata.run(f'do "{absolute_path}"')
    
    # Pull data out
    result_df = stata.pdataframe_from_data()
    
    return result_df