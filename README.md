# Getting Started with Stata in Fabric

## Requirements

* Stata 17+
* Windows

## Installations and Preparations

### 1. Installing Git & Downloading the Project

To download this project setup to your computer, you will use a version control tool called Git. 

1. Download and install Git for Windows here: [https://git-scm.com/install/windows](https://git-scm.com/install/windows)
2. Open **PowerShell** on your computer.
3. Open your File Explorer and navigate to the folder where you want this project to live.
4. Inside that folder, Shift-right-click and select "Open PowerShell window here"
4. Inside PowerShell, run the following command to download the project:
   ```powershell
   git clone https://github.com/Codyvanzandt/Fabric-Stata-Quickstart Fabric-Stata
   ```
This will automatically create a folder named `Fabric-Stata` containing all the files you need. Keep PowerShell open.

### 2. Installing the SQL Driver

Because we are securely connecting to the enterprise Microsoft Fabric Data Warehouse, your computer needs a specific Microsoft driver installed to translate the database connection.

1. Download the **ODBC Driver 18 for SQL Server (x64)** here: [Microsoft ODBC Driver Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17)
2. Open the downloaded `.msi` file and click through the standard Windows installation wizard (you can leave all default settings as they are).

### 3. Installing VS Code

VS Code is the integrated development environment (IDE) where you will write and run your Stata code.
* Install VS Code here: [https://code.visualstudio.com/](https://code.visualstudio.com/)

### 4. Installing Python & `uv`

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

### 5. Preparing VS Code

1. Launch **VS Code** (Windows key, type "VS Code")
2. In the top-left menu, select **File -> Open Folder**, and choose the `Fabric-Stata` folder you downloaded in Step 1.
3. VS Code needs a few extensions to support our workflow. Click the **Extensions** icon on the far left sidebar (it looks like four blocks with one tumbling away).
4. Search for and install the following extensions one by one (click "Install", wait until the Install button turns into a cog icon, indicating it has finished):
   * **Python** (by Microsoft)
   * **Jupyter** (by Microsoft)
   * **Fabric Data Engineering VS Code** (by Microsoft)
   * **Stata Enhanced** (by Kyle Barron)

### 6. Authenticating to Microsoft Fabric

1. Open the Command Palette in VS Code by pressing `Ctrl+Shift+P`.
2. Type **Fabric Data Engineering: Sign In** and hit Enter.
3. A web browser window will open. Log in using your standard company Microsoft credentials.
4. Return to VS Code. If prompted to "Set a local work folder," choose the `Fabric-Stata` folder.
5. Click the new **Fabric** icon on the left sidebar (it looks like a cursive 'S' mixed with a recycling symbol).
6. Click **Select Workspace**, and choose your designated Fabric workspace.

### 7. Preparing the Python Environment

1. In VS Code, open a terminal from the top menu by selecting **Terminal -> New Terminal**. It should automatically open in your project folder.
2. Create a dedicated virtual environment (an isolated workspace for this project's dependencies) by running:
   ```powershell
   uv venv --python 3.11
   ```
3. Install the required Python packages (the libraries needed to talk to Azure and Fabric) by running:
   ```powershell
   uv pip install -r requirements.txt
   ```

### 8. Configuring Your Settings

We need to tell the project where Stata is installed on your machine and which Fabric environment to point to.

1. Click the **Explorer** icon in the top left sidebar (it looks like two overlapping pieces of paper) to view your project files. You will find a file named `config.example.yaml`.
2. Right-click `config.example.yaml` and rename it to **`config.yaml`**.
3. Click `config.yaml` to open it. 
4. Find the full path to your Stata installation (e.g., `C:/Program Files/Stata18`). Update the Stata section of `config.yaml` to match your path and edition (keep the quotation marks):
   ```yaml
   stata:
     install_path: "C:/Program Files/Stata18"
     edition: "mp"
   ```
5. Further down the file, update the Fabric section with your workspace details.
   ```yaml
   fabric:
     warehouse_server: "<your-id>.datawarehouse.fabric.microsoft.com"
     warehouse_name: "Your_Workspace_Name"
     lakehouse_abfs_path: "abfss://Your_Workspace_Name@onelake.dfs.fabric.microsoft.com/Your_Workspace_Name.Lakehouse/Tables"
   ```
6. Save the file (`Ctrl+S`) and close the tab by clicking the 'X' next to the filename at the top.

## Preparing to Use Stata

You will use Jupyter Notebooks to conduct your analysis. Jupyter is an interactive document format that lets you run blocks of code one at a time and see the results immediately below them.

1. In the VS Code Explorer sidebar, right-click the **`src`** folder and select **New File**. 
2. Name the file anything you like, as long as it ends in `.ipynb` (for example, `analysis.ipynb` or `exploration.ipynb`). 
3. Click your newly created file to open it.
4. In the top right corner of the notebook window, click **Select Kernel**. 
5. Choose **Python Environments** from the dropdown menu, and then select the environment labeled **Fabric-Stata** (it should have a star next to it indicating it is the recommended workspace environment). 

You are now fully connected to Fabric and ready to write Stata code!

## Using Stata

You can create Stata do-files and Jupyter notebooks inside your **`src`** folder.

### Setup Your Jupyter Notebook

Create a notebook inside **`src`** folder.

Every notebook you create needs to include the following code block, which can also be found in **`src/example.ipynb`**:

```
%load_ext autoreload
%autoreload 2

from fabric_utils import read_table, run_stata_script, write_table, load_config

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

When you're ready to write your new data to Fabric, use the `write_table` function, passing in the dataframe created by `run_stata_script`. You'll also need to pass a Fabria lakehouse schema name and table name.

```python
write_table(processed_data, "schema_name", "table_name")
```


