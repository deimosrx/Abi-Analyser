# ⚡ ABI Analyzer — Smart Contract Risk Intelligence Tool

A modern command-line tool built in Python for analyzing **Ethereum smart contract ABIs**.  
`ABI Analyzer` helps **auditors**, **developers**, and **security researchers** quickly understand a contract’s structure, detect common vulnerabilities, and export beautiful Markdown reports.

---

## 🚀 Features

- 🧠 **Intelligent Function Analysis**  
  Detects dangerous functions (like `delegatecall`, `selfdestruct`, or unrestricted `transferFrom`) and highlights possible attack vectors.

- 📊 **Automatic Risk Classification**  
  Each function is classified by **risk level** and **complexity**, helping you prioritize audit focus.

- 🔍 **ERC Detection**  
  Identifies ERC standards implemented in the ABI (e.g., ERC20, ERC721, ERC1155).

- 🧩 **Function Search**  
  Search for any function by name or keyword within the ABI.

- 🧾 **Rich CLI Interface**  
  Built with [`rich`](https://github.com/Textualize/rich) — enjoy beautiful tables, colors, and interactive prompts.

- 📝 **Markdown Report Export**  
  Automatically export your analysis to a clean, well-formatted `.md` report.

---

## 🧰 Installation

Make sure you have **Python 3.10+** installed.

```bash
git clone https://github.com/deimosrx/Abi-Analyser.git
cd "Abi-Analyser/src"
pip install -r requirements.txt
```

## 💻 Usage

### ▶️ Running the Tool

Run the CLI from the **`src`** directory:

```bash
cd src
python cli.py
# You’ll see an interactive prompt:
# abi-analyzer >:
```

## 🧩 Available Commands

| Command | Description | Example |
|----------|--------------|----------|
| `load <path>` | Load an ABI JSON file for analysis | `load ./test.json` |
| `info` | Display a detailed summary of the currently loaded ABI | `info` |
| `analyze` | Perform automated risk and complexity analysis | `analyze` |
| `function <name>` | Inspect a specific function in depth | `function transfer` |
| `search <keyword>` | Search functions, events, or errors by keyword | `search approve` |
| `selectors` | List all function selectors (`keccak256` hashes) | `selectors` |
| `detect-erc` | Detect implemented ERC standards (e.g., ERC20, ERC721) | `detect-erc` |
| `export <path>` | Export a full Markdown report | `export ./analysis_report.md` |
| `help` | Display available commands and usage tips | `help` |
| `exit` / `quit` | Exit the application | `exit` |


## 🚀 Examples

Here are some common examples of how to use **ABI Analyzer** inside the interactive CLI:

### 1. Load an ABI file  
```bash
> load ./test.json  
Loads the ABI file from the provided path and prepares it for analysis.
```
---

### 2. Display ABI information
```bash
> info  
Shows a detailed summary of functions, events, errors, constructors, and fallbacks.
````
---

### 3. Analyze the ABI
```bash
> analyze  
Performs a deep analysis of the ABI to detect potential vulnerabilities and estimate code complexity.
```
---

### 4. Inspect a specific function  
```bash
> function transfer  
Displays the details of the `transfer` function, including inputs, outputs, and state mutability.
```
---

### 5. Search for keywords  
```bash
> search owner  
Searches for any ABI element (function, event, or error) containing the keyword `owner`.
```
---

### 6. View all function selectors  
```bash
> selectors  
Lists all function selectors with their encoded signatures.
```
---

### 7. Detect ERC standards  
``` bash
> detect-erc  
Attempts to identify whether the ABI follows ERC20, ERC721, or ERC1155 standards.
```
---

### 8. Export report  
```bash
> export ./analysis_report.md  
Generates a complete Markdown report containing ABI information, analysis, and risk assessment.
```
---

### 9. Exit the CLI
```bash
> exit  
Closes the interactive CLI session safely.
```
