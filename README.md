# Cr4cKen5 - BruteForce Security Suite

An interactive Python graphical user interface (GUI) built with `tkinter` to easily configure, preview, and launch command-line security testing tools (Nmap, DIRB, Wfuzz, Hydra, and SQLMap) on your Kali Linux system.

---

## Capabilities & Functions

* **Centralized Target Specification:** Enter a target IP or URL once in the header. The application dynamically cleans, sanitizes, and formats it for each specific tool requirement.
* **Modular Configuration Panel:**
  * **Nmap Port Scanner:** Configure timing parameters (`-T1` through `-T5`), service version detection, default audits, and OS fingerprinting.
  * **DIRB Web Mapper:** Audits web directory hierarchies. Includes wordlist file-browsing shortcuts.
  * **Wfuzz Parameter Fuzzer:** Map directories or web parameters using custom wordlists while filtering out specific HTTP status codes (e.g., `--hc 404`).
  * **Hydra Login Auditor:** Perform login auditing over multiple network protocols (`ssh`, `ftp`, `telnet`) and web-login forms (`http-get-form`, `http-post-form`).
  * **SQLMap Database Auditor:** Audit input variables and POST bodies (`--data`) for SQL injection vulnerabilities.
* **Vulnerability Parser & Correlation:** Normanizes and aggregates Nmap XML scan outputs and SQLMap local log sessions into a centralized interactive tree grid.
* **Sleek Reporting Engine:** Compiles parsed findings into a modern, responsive HTML report featuring threat summary metrics and remediation instructions.
* **Live Command Previewer:** Generates and displays the exact command syntax in real-time as configurations change.
* **Safe Terminal Execution Backend:** Instead of executing commands directly, the engine compiles them into temporary shell scripts (`.sh` on Linux, `.bat` on Windows) and runs them in a separate terminal. This preserves nested single/double quotes and URL characters without shell escaping errors.

---

## Installation & Deployment Guide

Instead of downloading ZIP files, you can clone the entire repository directly from GitHub to automatically bundle the scripts and the default fallback wordlists together.

```bash
# Clone the repository
git clone https://github.com/N3k0sint/Cr4cKen5.git

# Enter the project directory
cd Cr4cKen5
```

---

### Linux Setup (cracken5.py)

#### 1. Install System Dependencies
Before running the dashboard, verify you have Python Tkinter, a terminal emulator, and the target tools installed on your Linux / Kali system:
```bash
# Update repositories and install GUI dependencies
sudo apt update && sudo apt install -y python3-tk qterminal

# Verify target auditing tool installations
sudo apt install -y nmap dirb sqlmap hydra wfuzz
```

#### 2. Run the Dashboard
Ensure execution permissions are active and launch the Python script:
```bash
chmod +x cracken5.py
./cracken5.py
```
*(Alternatively, run `python3 cracken5.py`)*
