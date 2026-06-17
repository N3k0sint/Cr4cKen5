# Cr4cKen5 - BruteForce Security Guide

Welcome to the **Cr4cKen5** user manual. This guide outlines the capabilities of the dashboard, explains the configuration options for each auditing module, and details how the underlying execution backend functions.

---

## Table of Contents
1. [Overview & Layout](#1-overview--layout)
2. [Global Target Normalization](#2-global-target-normalization)
3. [Auditing Modules](#3-auditing-modules)
   - [Nmap Port Scanner](#nmap-port-scanner)
   - [DIRB Web Mapper](#dirb-web-mapper)
   - [Wfuzz Parameter Fuzzer](#wfuzz-parameter-fuzzer)
   - [Hydra Login Auditor](#hydra-login-auditor)
   - [SQLMap DB Auditor](#sqlmap-db-auditor)
   - [Audit Reports Tab](#audit-reports-tab)
4. [Backend Mechanics (Temporary Script Execution)](#4-backend-mechanics-temporary-script-execution)
5. [Vulnerability Aggregation & Reporting](#5-vulnerability-aggregation--reporting)
6. [Prerequisites & System Setup](#6-prerequisites--system-setup)
   - [Git Cloning Method](#git-cloning-method)
   - [Linux Environment Setup](#linux-environment-setup)
   - [Windows Environment Setup](#windows-environment-setup)
   - [Standalone Executable Packaging (.exe)](#standalone-executable-packaging-exe)

---

## 1. Overview & Layout

**Cr4cKen5** is an interactive, unified graphical interface written in Python (Tkinter) designed to streamline initial host enumeration and security auditing workflows. 

### Key Design Features:
* **Left-Hand Sidebar Navigation:** Seamlessly toggle between different modules without losing settings in other tabs.
* **Enterprise Dark Theme:** Styled using a clean, modern palette featuring deep slate backgrounds, indigo accents, and high-contrast monospaced command preview windows.
* **Live Command Previewer:** Dynamically builds and updates the exact command-line syntax in real time as you adjust inputs and checkboxes.
* **Detached Execution:** Spawns scans inside a native terminal emulator (e.g., `qterminal` or Windows `cmd.exe`), allowing you to view stdout in real time and run multiple tools concurrently.

---

## 2. Global Target Normalization

The target address specified in the header card (**Host Address / URL**) is automatically parsed and sanitized differently depending on the active module:

| Active Module | Expected Syntax | Auto-Sanitization Behavior | Example Input -> Output |
| :--- | :--- | :--- | :--- |
| **Nmap** | Hostname or IP | Strips `http://`, `https://`, paths, and query variables to resolve a clean IP/Domain. | `http://192.168.1.1/index.php` -> `192.168.1.1` |
| **DIRB** | Web Directory URL | Strips query variables; ensures it ends in a trailing slash. | `http://192.168.1.1/login.php` -> `http://192.168.1.1/` |
| **Wfuzz** | Target Fuzz URL | Strips query variables; appends `FUZZ` placeholder key. | `http://192.168.1.1/index.php` -> `http://192.168.1.1/FUZZ` |
| **Hydra** | Hostname or IP | Resolves target down to the domain/IP name. | `http://192.168.1.1/index.php` -> `192.168.1.1` |
| **SQLMap** | Full Target URL | Retains protocol scheme and paths; adds quotes to ensure query string parsing. | `192.168.1.1` -> `http://192.168.1.1` |

> [!TIP]
> The target input field automatically clears its default value (`127.0.0.1`) when focused, preventing accidental merge errors like `127.0.0.1http://...`.

---

## 3. Auditing Modules

### Nmap Port Scanner
Used to perform host discovery and network auditing.
* **Options:**
  * **Service Version Detection (`-sV`):** Probes open ports to determine service name and version details.
  * **Default Scan Scripts (`-sC`):** Executes standard Nmap Scripting Engine (NSE) scripts to check for common misconfigurations.
  * **OS Fingerprinting (`-O`):** Sends packet probes to determine the operating system (requires root/admin permissions).
  * **Timing Profiles (`-T1` to `-T5`):** Adjusts timing speeds (T4 is recommended for stable networks).

### DIRB Web Mapper
Used to locate hidden directories and files on web servers.
* **Options:**
  * **Dictionary Wordlist:** Specify the dictionary file paths. Defaults to `/usr/share/dirb/wordlists/common.txt` on Linux, and a built-in fallback wordlist extracted to `%TEMP%\cracken5_default_wordlist.txt` on Windows.
  * **Quiet Mode (`-S`):** Suppresses redundant messages and warnings during discovery.

### Wfuzz Parameter Fuzzer
Used to find web resources, paths, or fuzzed query parameters by replacing the `/FUZZ` string with wordlist entries.
* **Options:**
  * **Dictionary Wordlist:** Select a fuzzing dictionary. Defaults to `/usr/share/wfuzz/wordlist/general/common.txt` on Linux, and `%TEMP%\cracken5_default_wordlist.txt` on Windows.
  * **Hide HTTP Code (`--hc`):** Filters out unhelpful HTTP response codes (e.g., hiding `404` to only display positive matches).

### Hydra Login Auditor
Used to audit network authentication portals using brute-force mechanics.
* **Options:**
  * **Protocol:** Supports standard protocols (`ssh`, `ftp`, `telnet`) and web protocols (`http-get`, `http-get-form`, `http-post-form`).
  * **Web Form Parameters:** When a form protocol is selected, fields appear to configure the login path, body data structure (using `^USER^` and `^PASS^` placeholders), and the failure string criteria (e.g., `F=Authentication failed`).
  * **Tasks (`-t`):** Adjusts concurrent login threads. Enforces values within Hydra's safe boundaries (`4`, `8`, `16`, `32`, `64`).

### SQLMap DB Auditor
Used to check web parameters for database-level injection vulnerabilities.
* **Options:**
  * **Audit Risk Level:** Select tests ranging from `1` (safe default) to `3` (adds heavy or time-based payloads).
  * **Automated Batch Mode (`--batch`):** Suppresses user prompt questions, automatically choosing the default safe answers.
  * **Retrieve Active DB structure (`--current-db`):** Attempts to fetch and return the active database name.
  * **POST Data (`--data`):** Switch to testing HTTP POST inputs by providing the form payload string.
  * **Target Parameter (`-p`):** Tell SQLMap to focus testing on a single key, saving time.

### Audit Reports Tab
Used to analyze and visualize findings aggregated from automated scans.
* **Options:**
  * **Load / Refresh Findings:** Automatically scans local log locations and Nmap XML outputs to update the interface grid.
  * **Export HTML Report:** Compiles all findings into a responsive report dashboard and opens it in a browser window.
  * **Selection Pane:** Displays detailed extraction payloads and mitigation suggestions for the selected row item.

---

## 4. Backend Mechanics (Temporary Script Execution)

Standard command execution wrappers in Python often fail when dealing with complex nested characters. 

### How Cr4cKen5 Solves This:
1. When you click **EXECUTE SUITE**, the script generates a temporary launcher file inside the system temp directory (`/tmp/` on Linux, `%TEMP%` on Windows).
2. It writes a proper script header (`#!/bin/bash` or `@echo off`), inserts the exact command, and adds a pause command:
   * **Linux:**
     ```bash
     #!/bin/bash
     sqlmap -u 'http://...' --data="..." -p username
     echo
     echo 'Scan complete.'
     read -p 'Press Enter to close...'
     ```
   * **Windows:**
     ```cmd
     @echo off
     sqlmap -u 'http://...' --data="..." -p username
     echo.
     echo Scan complete.
     pause
     ```
3. It launches the temporary script inside a newly spawned visible terminal window, ensuring the GUI remains fully responsive.

---

## 5. Vulnerability Aggregation & Reporting

The reports engine performs multi-source correlation:
1. **Nmap XML Parsing:** Reads XML outputs to parse out open port records, service brands, and software versions. It assigns severities (e.g. Medium for insecure plain-text protocols, High for administrative service interfaces).
2. **SQLMap Logs parsing:** Evaluates active session log files located inside the standard local SQLMap outputs storage (`~/.local/share/sqlmap/output/*/log` or `~/.sqlmap/output/*/log` on Windows). It extracts injection types, vector parameters, techniques, and payloads, assigning a `Critical` severity level.
3. **HTML Reporting Module:** Aggregates findings and counts the threat metrics. It compiles these into an HTML report utilizing modern, responsive styles, complete with executive summary charts and remediation instructions.

---

## 6. Prerequisites & System Setup

### Git Cloning Method
Rather than manually transferring scripts, users can clone the repository to retrieve the complete environment (including files and default dictionary wordlists):
```bash
git clone https://github.com/N3k0sint/Cr4cKen5.git
cd Cr4cKen5
```

### Linux Environment Setup
Ensure the necessary system tools and python libraries are present:
```bash
# Update local packages
sudo apt update

# Install Tkinter python wrapper and QTerminal
sudo apt install -y python3-tk qterminal

# Verify CLI binaries are installed
sudo apt install -y nmap dirb wfuzz hydra sqlmap
```

To run the suite:
```bash
chmod +x cracken5.py
./cracken5.py
```

### Windows Environment Setup
1. **Python:** Install Python from python.org. Make sure to check **Add python.exe to PATH** and **tcl/tk and IDLE**.
2. **Binaries:** Download Nmap, SQLMap, Hydra, and Wfuzz. Extract them and add their directories to the Windows **Path** environment variable in your System Settings.
3. To run the suite:
   ```cmd
   python cracken5_win.py
   ```

### Standalone Executable Packaging (.exe)
You can package the Windows dashboard along with its built-in fallback wordlist into a single `.exe` executable file.

1. Install PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
2. Navigate to the project folder and run the compiler command:
   ```cmd
   pyinstaller --onefile --noconsole --add-data "default_wordlist.txt;." cracken5_win.py
   ```
3. The executable will be built inside:
   ```cmd
   dist\cracken5_win.exe
   ```
   You can copy this single `.exe` file to any other folder or machine to run it independently.
