# Getting Started with Stata in Fabric

## Requirements

* Stata 17+ (provides `pystata`)
* Windows
* ODBC Driver 18 for SQL Server
* Python 3.11+
* Microsoft Fabric / Azure login access

## Install the library from GitHub

Create a project folder and virtual environment, then install the package:

```powershell
mkdir Fabric-Stata
cd Fabric-Stata
uv venv --python 3.11
uv pip install "git+https://github.com/Codyvanzandt/Fabric-Stata-Quickstart.git"
uv pip install ipykernel
```

Or with pip:

```powershell
pip install "git+https://github.com/Codyvanzandt/Fabric-Stata-Quickstart.git"
```

Installing the package does **not** ship example notebooks or a config file. You create those in your own project folder (see below).

System dependencies such as the ODBC driver, Stata, and Azure authentication are not installed by pip.

To update later:

```powershell
uv pip install --force-reinstall --no-cache "git+https://github.com/Codyvanzandt/Fabric-Stata-Quickstart.git"
```

## Installations and Preparations

### 1. Installing the SQL Driver

Because we are securely connecting to the enterprise Microsoft Fabric Data Warehouse, your computer needs a specific Microsoft driver installed to translate the database connection.

1. Download the **ODBC Driver 18 for SQL Server (x64)** here: [Microsoft ODBC Driver Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17)
2. Open the downloaded `.msi` file and click through the standard Windows installation wizard (you can leave all default settings as they are).

### 2. Installing VS Code

VS Code is the integrated development environment (IDE) where you will write and run your Stata code.
* Install VS Code here: [https://code.visualstudio.com/](https://code.visualstudio.com/)

### 3. Installing Python & `uv`

Using Stata in Fabric requires a Python background process to handle the data transfer. To install and manage Python, we use an industry-standard tool called `uv`.

1. Inside PowerShell, run the following command to install `uv`:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. Close your PowerShell window, open a new one (Windows key, type "PowerShell"), and run this command to verify the installation was successful:
   ```powershell
   uv --version
   ```
   *(If successful, it will print out the current version number of uv).*
3. Finally, install Python 3.11 by running:
   ```powershell
   uv python install 3.11
   ```

### 4. Preparing VS Code

1. Launch **VS Code** (Windows key, type "VS Code")
2. In the top-left menu, select **File -> Open Folder**, and choose your `Fabric-Stata` project folder.
3. VS Code needs a few extensions to support our workflow. Click the **Extensions** icon on the far left sidebar (it looks like four blocks with one tumbling away).
4. Search for and install the following extensions one by one (click "Install", wait until the Install button turns into a cog icon, indicating it has finished):
   * **Python** (by Microsoft)
   * **Jupyter** (by Microsoft)
   * **Fabric Data Engineering VS Code** (by Microsoft)
   * **Stata Enhanced** (by Kyle Barron)

### 5. Authenticating to Microsoft Fabric

1. Open the Command Palette in VS Code by pressing `Ctrl+Shift+P`.
2. Type **Fabric Data Engineering: Sign In** and hit Enter.
3. A web browser window will open. Log in using your standard company Microsoft credentials.
4. Return to VS Code. If prompted to "Set a local work folder," choose your project folder.
5. Click the new **Fabric** icon on the left sidebar (it looks like a cursive 'S' mixed with a recycling symbol).
6. Click **Select Workspace**, and choose your designated Fabric workspace.

### 6. Create your `config.yaml`

`load_config()` looks for a file named **`config.yaml`** in your notebook's working directory (usually your project folder). Create that file yourself — it is not installed with the package.

1. In VS Code Explorer, create a new file named **`config.yaml`**.
2. Paste the following template and fill in your values:

```yaml
stata:
  install_path: "C:/Program Files/Stata18"
  edition: "mp"

fabric:
  warehouse_server: "<your-id>.datawarehouse.fabric.microsoft.com"
  warehouse_name: "Your_Warehouse_Or_Lakehouse_SQL_Name"
  lakehouse_abfs_path: "abfss://Your_Workspace_Name@onelake.dfs.fabric.microsoft.com/Your_Lakehouse_Name.Lakehouse"
```

3. Set `install_path` to your Stata install and `edition` to `mp`, `se`, or `be`.
4. Set the Fabric warehouse and lakehouse values for your workspace.
5. For `lakehouse_abfs_path`, use the lakehouse root only — **do not** add a trailing `/` or `/Tables` (the library appends `/Tables/...` when writing).
6. Save the file (`Ctrl+S`).

## Preparing to Use Stata

You will use Jupyter Notebooks to conduct your analysis. Jupyter is an interactive document format that lets you run blocks of code one at a time and see the results immediately below them.

1. In the VS Code Explorer sidebar, create a new notebook file ending in `.ipynb` (for example, `analysis.ipynb`).
2. Click your newly created file to open it.
3. In the top right corner of the notebook window, click **Select Kernel**.
4. Choose **Python Environments** from the dropdown menu, and then select the virtual environment for this project.

You are now fully connected to Fabric and ready to write Stata code!

## Using Stata

You can create Stata do-files and Jupyter notebooks in your project folder.

### Setup Your Jupyter Notebook

Every notebook you create needs to include the following code block:

```python
%load_ext autoreload
%autoreload 2

from fabric_stata import read_table, run_stata_script, write_table, load_config
import stata_setup

config = load_config()
stata_setup.config(config['stata']['install_path'], config['stata']['edition'])
```

This code prepares your environment to read data from Fabric, execute Stata code, and write tables back to Fabric.

### Read Data from Fabric

In a new code cell in your notebook, use the `read_table` function to read Fabric data:

```python
fabric_data = read_table("schema_name", "table_name")
```

Your Fabric credentials periodically expire. When that happens, a browser Window will open and ask you to re-authenciate to Fabric.

### Run your Stata Code

In another code cell, use the `run_stata_script` function to execute a Stata do-file, passing in the dataframe created by `read_table` and the path to your Stata file. The path should be relative to the location of your Jupyter notebook.

Don't use `use` in your do-file. The Python code loads the data into Stata as if you had opened the dataset manually.
At the end of your `.do` file, use the `keep` command to select the final columns you want to write to Fabric.

```python
processed_data = run_stata_script(fabric_data, "path/to/your/stata/file.do")
```

## Write the Data to Fabric

When you're ready to write your new data to Fabric, use the `write_table` function with the dataframe from `run_stata_script` and a lakehouse table name. For non-schema-enabled lakehouses, omit schema:

```python
write_table(processed_data, "table_name")
```

For schema-enabled lakehouses, pass the schema:

```python
write_table(processed_data, "table_name", schema="dbo")
```
