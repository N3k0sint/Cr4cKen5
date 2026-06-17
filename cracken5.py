#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import shutil
import tempfile
import os
import json
import re
import xml.etree.ElementTree as ET
import glob
import webbrowser

class CyberDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Cr4cKen5 - Enterprise Security Suite")
        self.root.geometry("900x650")
        self.root.minsize(850, 580)
        
        # --- Enterprise Dark Theme Palette ---
        self.bg_color = "#0f172a"          # Deep Slate Blue
        self.card_color = "#1e293b"        # Lighter Slate for containers
        self.sidebar_color = "#090d16"     # Darker navy-black for sidebar
        self.text_color = "#94a3b8"        # Soft gray-blue for labels
        self.header_color = "#f8fafc"      # Clean off-white for titles
        self.accent_color = "#6366f1"      # Modern Indigo
        self.accent_hover = "#4f46e5"      # Darker Indigo for active states
        self.button_color = "#334155"      # Secondary gray-slate button
        self.button_hover = "#475569"
        
        self.root.configure(bg=self.bg_color)
        
        # Config Storage Configuration
        self.config_file = os.path.expanduser("~/.cracken5_config.json")
        self.config_data = self.load_config()
        
        # Apply Base Styling
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TEntry", fieldbackground=self.card_color, foreground=self.header_color, bordercolor=self.button_color)
        self.style.configure("TCombobox", fieldbackground=self.card_color, background=self.button_color, foreground=self.header_color)
        
        # Configure Main Grid Layout
        self.root.columnconfigure(0, minsize=200, weight=0) # Sidebar
        self.root.columnconfigure(1, weight=1)             # Main Content
        self.root.rowconfigure(0, weight=1)
        
        # Initialize active tab index tracker
        self.active_tab = 0
        
        # Intercept window close to save current settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- 1. LEFT SIDEBAR PANEL ---
        self.sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Brand Header
        brand_label = tk.Label(self.sidebar, text="Cr4cKen5", font=("Segoe UI", 16, "bold"), bg=self.sidebar_color, fg=self.header_color)
        brand_label.pack(pady=(25, 5), anchor="w", padx=20)
        sub_label = tk.Label(self.sidebar, text="ENTERPRISE AUDIT SUITE", font=("Segoe UI", 8, "bold"), bg=self.sidebar_color, fg=self.accent_color)
        sub_label.pack(pady=(0, 20), anchor="w", padx=20)
        
        # Navigation Buttons
        self.nav_buttons = []
        nav_options = [
            ("Nmap Port Scanner", 0),
            ("DIRB Web Mapper", 1),
            ("Wfuzz Parameter Fuzzer", 2),
            ("Hydra Login Auditor", 3),
            ("SQLMap DB Auditor", 4),
            ("Audit Reports", 5)
        ]
        
        for name, idx in nav_options:
            btn = tk.Button(self.sidebar, text=name, font=("Segoe UI", 10, "normal"), 
                            bg=self.sidebar_color, fg=self.text_color, activebackground=self.accent_color,
                            activeforeground=self.header_color, bd=0, anchor="w", padx=20, pady=12,
                            command=lambda i=idx: self.switch_tab(i))
            btn.pack(fill="x")
            # Hover bindings
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_leave(b))
            self.nav_buttons.append(btn)
            
        # --- 2. MAIN CONTENT AREA ---
        self.main_container = tk.Frame(self.root, bg=self.bg_color, padx=25, pady=20)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        
        # 2a. Global Target Spec (Top Card)
        self.setup_target_card()
        
        # 2c. Command Preview & Action Card (Bottom) - Set up early to define cmd_preview_var
        self.setup_action_card()
        
        # 2b. Module Card Container (Holds individual module frames)
        self.module_container = tk.Frame(self.main_container, bg=self.card_color, bd=1, relief="flat", highlightbackground=self.button_color, highlightcolor=self.button_color, highlightthickness=1)
        self.module_container.grid(row=1, column=0, sticky="nsew", pady=(15, 15))
        
        # Setup Module Frames
        self.module_frames = []
        self.setup_nmap_frame()
        self.setup_dirb_frame()
        self.setup_wfuzz_frame()
        self.setup_hydra_frame()
        self.setup_sqlmap_frame()
        self.setup_reports_frame()
        
        # Initialize default view
        self.switch_tab(0)

    # --- Sidebar Navigation Helpers ---
    def switch_tab(self, index):
        # Hide current active frame
        self.module_frames[self.active_tab].pack_forget()
        
        # Reset previous active button styles
        self.nav_buttons[self.active_tab].configure(bg=self.sidebar_color, fg=self.text_color)
        
        # Set new active tab
        self.active_tab = index
        self.module_frames[self.active_tab].pack(fill="both", expand=True, padx=20, pady=20)
        
        # Style active button
        self.nav_buttons[self.active_tab].configure(bg=self.card_color, fg=self.header_color)
        
        # Disable Command Executor Footer Card for Audit Reports Tab
        if self.active_tab == 5:
            self.cmd_preview_var.set("No execution required for Audit Reports. Use controls inside reports panel.")
            self.run_button.configure(state="disabled", bg=self.button_color)
        else:
            self.run_button.configure(state="normal", bg=self.accent_color)
            self.update_previews()

    def on_nav_enter(self, button):
        # Highlight on hover unless it's the active tab
        btn_idx = self.nav_buttons.index(button)
        if btn_idx != self.active_tab:
            button.configure(bg="#152136", fg=self.header_color)

    def on_nav_leave(self, button):
        # Restore state on mouse leave
        btn_idx = self.nav_buttons.index(button)
        if btn_idx != self.active_tab:
            button.configure(bg=self.sidebar_color, fg=self.text_color)

    # --- Target Specifications (Header Card) ---
    def setup_target_card(self):
        target_card = tk.Frame(self.main_container, bg=self.card_color, padx=15, pady=15, bd=1, highlightbackground=self.button_color, highlightcolor=self.button_color, highlightthickness=1)
        target_card.grid(row=0, column=0, sticky="ew")
        target_card.columnconfigure(1, weight=1)
        
        tk.Label(target_card, text="TARGET HOST SPECIFICATION", font=("Segoe UI", 8, "bold"), bg=self.card_color, fg=self.accent_color).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        tk.Label(target_card, text="Host Address / URL:", font=("Segoe UI", 10), bg=self.card_color, fg=self.text_color).grid(row=1, column=0, sticky="w", padx=(0, 10))
        
        self.target_var = tk.StringVar(value=self.config_data.get("target", "127.0.0.1"))
        self.target_entry = tk.Entry(target_card, textvariable=self.target_var, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 11), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.target_entry.grid(row=1, column=1, sticky="ew", ipady=5, ipadx=5)
        self.target_entry.bind("<KeyRelease>", self.update_previews)
        self.target_entry.bind("<FocusIn>", self.clear_default_target)

    def clear_default_target(self, event=None):
        if self.target_var.get() == "127.0.0.1":
            self.target_var.set("")

    # --- Command Run & Preview Panel (Footer Card) ---
    def setup_action_card(self):
        action_card = tk.Frame(self.main_container, bg=self.card_color, padx=15, pady=15, bd=1, highlightbackground=self.button_color, highlightcolor=self.button_color, highlightthickness=1)
        action_card.grid(row=2, column=0, sticky="ew")
        action_card.columnconfigure(0, weight=1)
        
        tk.Label(action_card, text="GENERATED SHELL COMMAND PREVIEW", font=("Segoe UI", 8, "bold"), bg=self.card_color, fg=self.accent_color).grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # CLI Previewer
        self.cmd_preview_var = tk.StringVar()
        self.cmd_entry = tk.Entry(action_card, textvariable=self.cmd_preview_var, state="readonly", bg=self.bg_color, fg=self.header_color, readonlybackground=self.bg_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.cmd_entry.grid(row=1, column=0, sticky="ew", ipady=6, ipadx=5)
        
        # Execution Button
        self.run_button = tk.Button(action_card, text="EXECUTE SUITE", font=("Segoe UI", 10, "bold"), bg=self.accent_color, fg=self.header_color, activebackground=self.accent_hover, activeforeground=self.header_color, bd=0, cursor="hand2", padx=20, command=self.execute_command)
        self.run_button.grid(row=1, column=1, padx=(15, 0), sticky="ns")

    # --- MODULE: NMAP ---
    def setup_nmap_frame(self):
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        tk.Label(frame, text="NMAP AUDITING OPTIONS", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 15))
        
        # Checkboxes Container
        opts_frame = tk.Frame(frame, bg=self.card_color)
        opts_frame.pack(anchor="w")
        
        self.nmap_sv = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Detect active service versions (-sV)", variable=self.nmap_sv, command=self.update_previews).pack(anchor="w", pady=5)
        
        self.nmap_sc = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Launch default audit scripts (-sC)", variable=self.nmap_sc, command=self.update_previews).pack(anchor="w", pady=5)
        
        self.nmap_o = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Perform OS fingerprinting (-O - Requires Root)", variable=self.nmap_o, command=self.update_previews).pack(anchor="w", pady=5)
        
        # Scan Timing Dropdown
        speed_frame = tk.Frame(frame, bg=self.card_color, pady=15)
        speed_frame.pack(anchor="w")
        tk.Label(speed_frame, text="Scan Timing Profile:", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        
        self.nmap_timing = tk.StringVar(value="-T4")
        timing_combo = ttk.Combobox(speed_frame, textvariable=self.nmap_timing, values=["-T1", "-T2", "-T3", "-T4", "-T5"], width=8, state="readonly")
        timing_combo.grid(row=0, column=1, padx=10)
        timing_combo.bind("<<ComboboxSelected>>", self.update_previews)

    # --- MODULE: DIRB ---
    def setup_dirb_frame(self):
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        tk.Label(frame, text="DIRB DIRECTORY MAPPER", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 15))
        
        path_frame = tk.Frame(frame, bg=self.card_color)
        path_frame.pack(fill="x", pady=5)
        tk.Label(path_frame, text="Target Dictionary Wordlist:", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        
        entry_frame = tk.Frame(path_frame, bg=self.card_color)
        entry_frame.pack(fill="x")
        self.wordlist_var = tk.StringVar(value=self.config_data.get("dirb_wl", "/usr/share/dirb/wordlists/common.txt"))
        self.wordlist_entry = tk.Entry(entry_frame, textvariable=self.wordlist_var, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.wordlist_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self.wordlist_entry.bind("<KeyRelease>", self.update_previews)
        
        browse_btn = tk.Button(entry_frame, text="Browse...", font=("Segoe UI", 9), bg=self.button_color, fg=self.header_color, activebackground=self.button_hover, activeforeground=self.header_color, bd=0, padx=15, command=lambda: self.browse_wordlist(self.wordlist_var))
        browse_btn.pack(side="right")
        
        self.dirb_silent = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Suppress warnings / Quiet mode (-S)", variable=self.dirb_silent, command=self.update_previews).pack(anchor="w", pady=15)

    # --- MODULE: WFUZZ ---
    def setup_wfuzz_frame(self):
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        tk.Label(frame, text="WFUZZ PARAMETER FUZZER", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 5))
        tk.Label(frame, text="Note: Target URL automatically gets '/FUZZ' appended to it.", font=("Segoe UI", 9, "italic"), bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 15))
        
        path_frame = tk.Frame(frame, bg=self.card_color)
        path_frame.pack(fill="x", pady=5)
        tk.Label(path_frame, text="Target Dictionary Wordlist:", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        
        entry_frame = tk.Frame(path_frame, bg=self.card_color)
        entry_frame.pack(fill="x")
        self.wfuzz_wl_var = tk.StringVar(value=self.config_data.get("wfuzz_wl", "/usr/share/wfuzz/wordlist/general/common.txt"))
        self.wfuzz_wl_entry = tk.Entry(entry_frame, textvariable=self.wfuzz_wl_var, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.wfuzz_wl_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self.wfuzz_wl_entry.bind("<KeyRelease>", self.update_previews)
        
        browse_btn = tk.Button(entry_frame, text="Browse...", font=("Segoe UI", 9), bg=self.button_color, fg=self.header_color, activebackground=self.button_hover, activeforeground=self.header_color, bd=0, padx=15, command=lambda: self.browse_wordlist(self.wfuzz_wl_var))
        browse_btn.pack(side="right")
        
        filter_frame = tk.Frame(frame, bg=self.card_color, pady=15)
        filter_frame.pack(fill="x", anchor="w")
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        # Row 0: Hide Code & Hide Characters
        tk.Label(filter_frame, text="Hide HTTP Code (--hc):", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.wfuzz_hc = tk.StringVar(value=self.config_data.get("wfuzz_hc", "404"))
        hc_entry = tk.Entry(filter_frame, textvariable=self.wfuzz_hc, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), width=10, bd=0, highlightbackground=self.button_color, highlightthickness=1)
        hc_entry.grid(row=0, column=1, padx=(10, 20), sticky="w", ipady=3, ipadx=5)
        hc_entry.bind("<KeyRelease>", self.update_previews)
        
        tk.Label(filter_frame, text="Hide Char Size (--hh):", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", pady=5)
        self.wfuzz_hh = tk.StringVar(value=self.config_data.get("wfuzz_hh", ""))
        hh_entry = tk.Entry(filter_frame, textvariable=self.wfuzz_hh, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), width=10, bd=0, highlightbackground=self.button_color, highlightthickness=1)
        hh_entry.grid(row=0, column=3, padx=10, sticky="w", ipady=3, ipadx=5)
        hh_entry.bind("<KeyRelease>", self.update_previews)
        
        # Row 1: Hide Words & Hide Lines
        tk.Label(filter_frame, text="Hide Word Count (--hw):", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.wfuzz_hw = tk.StringVar(value=self.config_data.get("wfuzz_hw", ""))
        hw_entry = tk.Entry(filter_frame, textvariable=self.wfuzz_hw, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), width=10, bd=0, highlightbackground=self.button_color, highlightthickness=1)
        hw_entry.grid(row=1, column=1, padx=(10, 20), sticky="w", ipady=3, ipadx=5)
        hw_entry.bind("<KeyRelease>", self.update_previews)
        
        tk.Label(filter_frame, text="Hide Line Count (--hl):", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", pady=5)
        self.wfuzz_hl = tk.StringVar(value=self.config_data.get("wfuzz_hl", ""))
        hl_entry = tk.Entry(filter_frame, textvariable=self.wfuzz_hl, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), width=10, bd=0, highlightbackground=self.button_color, highlightthickness=1)
        hl_entry.grid(row=1, column=3, padx=10, sticky="w", ipady=3, ipadx=5)
        hl_entry.bind("<KeyRelease>", self.update_previews)

    # --- MODULE: HYDRA ---
    def setup_hydra_frame(self):
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        tk.Label(frame, text="HYDRA LOGIN BRUTE-FORCE AUDITOR", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 15))
        
        grid_frame = tk.Frame(frame, bg=self.card_color)
        grid_frame.pack(fill="x", pady=5)
        grid_frame.columnconfigure(1, weight=1)
        
        # Protocol
        tk.Label(grid_frame, text="Protocol:", bg=self.card_color, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=5)
        self.hydra_proto = tk.StringVar(value="ssh")
        proto_combo = ttk.Combobox(grid_frame, textvariable=self.hydra_proto, values=["ssh", "ftp", "telnet", "http-get", "http-get-form", "http-post-form"], width=15, state="readonly")
        proto_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        proto_combo.bind("<<ComboboxSelected>>", self.on_hydra_proto_changed)
        
        # Username
        tk.Label(grid_frame, text="Username:", bg=self.card_color, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=5)
        
        user_frame = tk.Frame(grid_frame, bg=self.card_color)
        user_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        self.hydra_user_is_list = tk.BooleanVar(value=self.config_data.get("hydra_user_is_list", False))
        self.hydra_user = tk.StringVar(value=self.config_data.get("hydra_user", "admin"))
        
        self.hydra_user_entry = tk.Entry(user_frame, textvariable=self.hydra_user, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), width=30, bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.hydra_user_entry.pack(side="left", ipady=3, ipadx=5)
        self.hydra_user_entry.bind("<KeyRelease>", self.update_previews)
        
        self.hydra_user_browse = tk.Button(user_frame, text="Browse...", font=("Segoe UI", 9), bg=self.button_color, fg=self.header_color, activebackground=self.button_hover, activeforeground=self.header_color, bd=0, padx=10, command=lambda: self.browse_wordlist(self.hydra_user))
        self.hydra_user_browse.pack(side="left", padx=10)
        
        tk.Checkbutton(user_frame, text="Use Wordlist File (-L)", variable=self.hydra_user_is_list, bg=self.card_color, fg=self.text_color, activebackground=self.card_color, activeforeground=self.text_color, selectcolor=self.bg_color, command=self.on_hydra_user_mode_changed).pack(side="left", padx=5)
        
        # Tasks (-t)
        tk.Label(grid_frame, text="Tasks (-t):", bg=self.card_color, fg=self.text_color).grid(row=2, column=0, sticky="w", pady=5)
        
        tasks_frame = tk.Frame(grid_frame, bg=self.card_color)
        tasks_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        self.hydra_tasks = tk.StringVar(value="16")
        tasks_combo = ttk.Combobox(tasks_frame, textvariable=self.hydra_tasks, values=["4", "8", "16", "32", "64"], width=8, state="readonly")
        tasks_combo.pack(side="left")
        tasks_combo.bind("<<ComboboxSelected>>", self.update_previews)
        
        self.hydra_exit_first = tk.BooleanVar(value=self.config_data.get("hydra_exit_first", False))
        tk.Checkbutton(tasks_frame, text="Stop on first success (-f)", variable=self.hydra_exit_first, bg=self.card_color, fg=self.text_color, activebackground=self.card_color, activeforeground=self.text_color, selectcolor=self.bg_color, command=self.update_previews).pack(side="left", padx=20)
        
        # Dynamic Web Form Options Frame (initially hidden)
        self.web_form_frame = tk.Frame(frame, bg=self.card_color)
        self.web_form_frame.columnconfigure(1, weight=1)
        
        # Form Path
        tk.Label(self.web_form_frame, text="Form Path:", bg=self.card_color, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=5)
        self.hydra_form_path = tk.StringVar(value="/index.php?page=login.php")
        self.hydra_form_path_entry = tk.Entry(self.web_form_frame, textvariable=self.hydra_form_path, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, width=35, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.hydra_form_path_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5, ipady=3)
        self.hydra_form_path_entry.bind("<KeyRelease>", self.update_previews)
        
        # Form Body
        tk.Label(self.web_form_frame, text="Form Body:", bg=self.card_color, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=5)
        self.hydra_form_body = tk.StringVar(value="username=^USER^&password=^PASS^&Login=Login")
        self.hydra_form_body_entry = tk.Entry(self.web_form_frame, textvariable=self.hydra_form_body, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, width=35, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.hydra_form_body_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5, ipady=3)
        self.hydra_form_body_entry.bind("<KeyRelease>", self.update_previews)
        
        # Failure String
        tk.Label(self.web_form_frame, text="Fail Match:", bg=self.card_color, fg=self.text_color).grid(row=2, column=0, sticky="w", pady=5)
        self.hydra_form_fail = tk.StringVar(value="F=username is incorrect")
        self.hydra_form_fail_entry = tk.Entry(self.web_form_frame, textvariable=self.hydra_form_fail, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, width=35, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.hydra_form_fail_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5, ipady=3)
        self.hydra_form_fail_entry.bind("<KeyRelease>", self.update_previews)
        
        # Wordlist Selector (Bottom of Hydra View)
        self.wl_container = tk.Frame(frame, bg=self.card_color)
        self.wl_container.pack(fill="x", side="bottom", pady=(15, 0))
        
        tk.Label(self.wl_container, text="Password Wordlist:", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        wl_frame = tk.Frame(self.wl_container, bg=self.card_color)
        wl_frame.pack(fill="x")
        self.hydra_wl_var = tk.StringVar(value=self.config_data.get("hydra_wl", "/usr/share/wordlists/rockyou.txt"))
        self.hydra_wl_entry = tk.Entry(wl_frame, textvariable=self.hydra_wl_var, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.hydra_wl_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self.hydra_wl_entry.bind("<KeyRelease>", self.update_previews)
        
        browse_wl_btn = tk.Button(wl_frame, text="Browse...", font=("Segoe UI", 9), bg=self.button_color, fg=self.header_color, activebackground=self.button_hover, activeforeground=self.header_color, bd=0, padx=15, command=lambda: self.browse_wordlist(self.hydra_wl_var))
        browse_wl_btn.pack(side="right")
        
        # Initialize Browse button state
        self.on_hydra_user_mode_changed()

    def on_hydra_proto_changed(self, event=None):
        proto = self.hydra_proto.get()
        if "form" in proto:
            self.web_form_frame.pack(fill="x", pady=5)
        else:
            self.web_form_frame.pack_forget()
        self.update_previews()

    def on_hydra_user_mode_changed(self):
        if self.hydra_user_is_list.get():
            self.hydra_user_browse.configure(state="normal")
        else:
            self.hydra_user_browse.configure(state="disabled")
        self.update_previews()

    # --- MODULE: SQLMAP ---
    def setup_sqlmap_frame(self):
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        tk.Label(frame, text="SQLMAP AUDITING SETTINGS", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 15))
        
        config_frame = tk.Frame(frame, bg=self.card_color)
        config_frame.pack(anchor="w")
        
        tk.Label(config_frame, text="Audit Risk Level (1-3):", bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        self.sql_risk = tk.StringVar(value="1")
        risk_combo = ttk.Combobox(config_frame, textvariable=self.sql_risk, values=["1", "2", "3"], width=5, state="readonly")
        risk_combo.grid(row=0, column=1, padx=10, pady=5)
        risk_combo.bind("<<ComboboxSelected>>", self.update_previews)
        
        self.sql_batch = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Automated Batch Mode (--batch)", variable=self.sql_batch, command=self.update_previews).pack(anchor="w", pady=5)
        
        self.sql_current_db = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Retrieve active database structure (--current-db)", variable=self.sql_current_db, command=self.update_previews).pack(anchor="w", pady=5)

        self.sql_dbs = tk.BooleanVar(value=self.config_data.get("sql_dbs", True))
        ttk.Checkbutton(frame, text="Retrieve database list (--dbs)", variable=self.sql_dbs, command=self.update_previews).pack(anchor="w", pady=5)

        # POST Payload Fields
        tk.Label(frame, text="POST Payload Configuration (Optional):", font=("Segoe UI", 11, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(15, 5))
        
        data_frame = tk.Frame(frame, bg=self.card_color)
        data_frame.pack(fill="x", pady=5)
        data_frame.columnconfigure(1, weight=1)
        
        # POST Body
        tk.Label(data_frame, text="POST Data (--data):", bg=self.card_color, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=5)
        self.sql_data = tk.StringVar(value="")
        self.sql_data_entry = tk.Entry(data_frame, textvariable=self.sql_data, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.sql_data_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5, ipady=3)
        self.sql_data_entry.bind("<KeyRelease>", self.update_previews)
        
        # Target Param
        tk.Label(data_frame, text="Target Param (-p):", bg=self.card_color, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=5)
        self.sql_param = tk.StringVar(value="")
        self.sql_param_entry = tk.Entry(data_frame, textvariable=self.sql_param, bg=self.bg_color, fg=self.header_color, insertbackground=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1)
        self.sql_param_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=3, ipadx=5)
        self.sql_param_entry.bind("<KeyRelease>", self.update_previews)

    # --- Helper Functions ---
    def browse_wordlist(self, target_variable):
        initial_dir = "/usr/share/wordlists/"
        selected_file = filedialog.askopenfilename(initialdir=initial_dir, title="Select Wordlist File")
        if selected_file:
            target_variable.set(selected_file)
            self.update_previews()

    def get_generated_command(self):
        raw_target = self.target_var.get().strip()
        if not raw_target:
            return ""
            
        # Sanitize target if user accidentally pasted a URL behind default text (e.g. 127.0.0.1http://...)
        if "http://" in raw_target:
            raw_target = "http://" + raw_target.split("http://")[-1]
        elif "https://" in raw_target:
            raw_target = "https://" + raw_target.split("https://")[-1]
            
        # Parse Hostname / URL cleanly
        from urllib.parse import urlparse
        has_scheme = raw_target.startswith("http://") or raw_target.startswith("https://")
        parsed = urlparse(raw_target if has_scheme else f"http://{raw_target}")
        
        clean_host = parsed.hostname or parsed.netloc or raw_target
        if not clean_host:
            clean_host = raw_target
            
        clean_url = raw_target if has_scheme else f"http://{raw_target}"
        
        if self.active_tab == 0: # Nmap
            flags = []
            if self.nmap_sv.get(): flags.append("-sV")
            if self.nmap_sc.get(): flags.append("-sC")
            if self.nmap_o.get(): flags.append("-O")
            flags.append(self.nmap_timing.get())
            return f"nmap {' '.join(flags)} -oX /tmp/cracken5_nmap.xml {clean_host}"
            
        elif self.active_tab == 1: # DIRB
            flags = []
            if self.dirb_silent.get(): flags.append("-S")
            wordlist = self.wordlist_var.get().strip()
            if "?" in clean_url:
                clean_url = clean_url.split("?")[0]
            if clean_url.endswith(".php") or clean_url.endswith(".html"):
                clean_url = "/".join(clean_url.split("/")[:-1]) + "/"
            return f"dirb {clean_url} {wordlist} {' '.join(flags)}".strip()
            
        elif self.active_tab == 2: # Wfuzz
            wl = self.wfuzz_wl_var.get().strip()
            if "?" in clean_url:
                clean_url = clean_url.split("?")[0]
            if not clean_url.endswith("/"):
                clean_url += "/"
                
            flags = ["-c", f"-z file,{wl}"]
            hc = self.wfuzz_hc.get().strip()
            if hc:
                flags.append(f"--hc {hc}")
            hh = self.wfuzz_hh.get().strip()
            if hh:
                flags.append(f"--hh {hh}")
            hw = self.wfuzz_hw.get().strip()
            if hw:
                flags.append(f"--hw {hw}")
            hl = self.wfuzz_hl.get().strip()
            if hl:
                flags.append(f"--hl {hl}")
                
            return f"wfuzz {' '.join(flags)} {clean_url}FUZZ"
            
        elif self.active_tab == 3: # Hydra
            user = self.hydra_user.get().strip()
            wl = self.hydra_wl_var.get().strip()
            proto = self.hydra_proto.get().strip()
            tasks = self.hydra_tasks.get().strip()
            
            # Setup User Option (-l or -L)
            user_opt = f"-L {user}" if self.hydra_user_is_list.get() else f"-l {user}"
            
            # Setup exit first Option (-f)
            exit_opt = " -f" if self.hydra_exit_first.get() else ""
            
            base_cmd = f"hydra -t {tasks}{exit_opt} {user_opt} -P {wl}"
            if "form" in proto:
                path = self.hydra_form_path.get().strip()
                body = self.hydra_form_body.get().strip()
                fail = self.hydra_form_fail.get().strip()
                return f"{base_cmd} {clean_host} {proto} \"{path}:{body}:{fail}\""
            else:
                return f"{base_cmd} {clean_host} {proto}"
            
        elif self.active_tab == 4: # SQLMap
            flags = [f"--risk={self.sql_risk.get()}"]
            if self.sql_batch.get(): flags.append("--batch")
            if self.sql_current_db.get(): flags.append("--current-db")
            if self.sql_dbs.get(): flags.append("--dbs")
            
            post_data = self.sql_data.get().strip()
            if post_data:
                flags.append(f"--data=\"{post_data}\"")
                
            target_param = self.sql_param.get().strip()
            if target_param:
                flags.append(f"-p {target_param}")
                
            return f"sqlmap -u '{clean_url}' {' '.join(flags)}"
            
        return ""

    def update_previews(self, event=None):
        if self.active_tab == 5:
            return
        cmd = self.get_generated_command()
        self.cmd_preview_var.set(cmd)
        self.validate_filepaths()

    def execute_command(self):
        cmd = self.cmd_preview_var.get()
        if not cmd:
            messagebox.showerror("Error", "No command generated. Check configurations.")
            return
            
        # Generate temporary bash script to preserve command quote parsing
        script_content = f"#!/bin/bash\n{cmd}\necho\necho 'Scan complete.'\nread -p 'Press Enter to close...'\n"
        
        try:
            fd, temp_path = tempfile.mkstemp(suffix=".sh", prefix="cracken5_")
            with open(temp_path, "w") as f:
                f.write(script_content)
            os.chmod(temp_path, 0o755)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create temporary launch script:\n{str(e)}")
            return
            
        if shutil.which("qterminal"):
            exec_args = ["qterminal", "-e", "bash", temp_path]
        elif shutil.which("xfce4-terminal"):
            exec_args = ["xfce4-terminal", "-e", "bash", temp_path]
        elif shutil.which("xterm"):
            exec_args = ["xterm", "-bg", "black", "-fg", "green", "-title", "Cr4cKen5 Attack Window", "-e", "bash", temp_path]
        else:
            messagebox.showerror("Dependency Error", "No compatible terminal (qterminal, xfce4-terminal, or xterm) found.")
            return
        
        try:
            subprocess.Popen(exec_args)
        except Exception as e:
            messagebox.showerror("Execution Failed", f"Could not launch shell window:\n{str(e)}")

    # --- Profile Storage & Validation Helpers ---
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        try:
            config = {
                "target": self.target_var.get().strip(),
                "dirb_wl": self.wordlist_var.get().strip(),
                "wfuzz_wl": self.wfuzz_wl_var.get().strip(),
                "hydra_wl": self.hydra_wl_var.get().strip(),
                "wfuzz_hc": self.wfuzz_hc.get().strip(),
                "wfuzz_hh": self.wfuzz_hh.get().strip(),
                "wfuzz_hw": self.wfuzz_hw.get().strip(),
                "wfuzz_hl": self.wfuzz_hl.get().strip(),
                "hydra_user": self.hydra_user.get().strip(),
                "hydra_user_is_list": self.hydra_user_is_list.get(),
                "hydra_exit_first": self.hydra_exit_first.get(),
                "sql_dbs": self.sql_dbs.get()
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def on_close(self):
        self.save_config()
        self.root.destroy()

    def validate_filepaths(self):
        # List of tuple configuration fields: (Entry Widget, Variable)
        paths_to_validate = [
            (self.wordlist_entry, self.wordlist_var),
            (self.wfuzz_wl_entry, self.wfuzz_wl_var),
            (self.hydra_wl_entry, self.hydra_wl_var)
        ]
        
        # Validate username wordlist only if checked
        if self.hydra_user_is_list.get():
            paths_to_validate.append((self.hydra_user_entry, self.hydra_user))
        else:
            self.hydra_user_entry.configure(bg=self.bg_color)
            
        for entry, var in paths_to_validate:
            path = var.get().strip()
            if not path:
                entry.configure(bg=self.bg_color) # Default empty
            elif os.path.isfile(path):
                entry.configure(bg=self.bg_color) # Valid
            else:
                entry.configure(bg="#450a0a") # Invalid / Highlight red

    # --- MODULE: AUDIT REPORTS ---
    def setup_reports_frame(self):
        self.all_findings = []
        frame = tk.Frame(self.module_container, bg=self.card_color)
        self.module_frames.append(frame)
        
        # Header
        tk.Label(frame, text="VULNERABILITY AUDIT LOGS & REPORTS", font=("Segoe UI", 14, "bold"), bg=self.card_color, fg=self.header_color).pack(anchor="w", pady=(0, 15))
        
        # Action Controls
        control_frame = tk.Frame(frame, bg=self.card_color)
        control_frame.pack(fill="x", pady=(0, 15))
        
        load_btn = tk.Button(control_frame, text="Load / Refresh Findings", font=("Segoe UI", 10, "bold"), bg=self.accent_color, fg=self.header_color, activebackground=self.accent_hover, activeforeground=self.header_color, bd=0, padx=15, pady=8, command=self.load_findings)
        load_btn.pack(side="left", padx=(0, 10))
        
        report_btn = tk.Button(control_frame, text="Export HTML Report", font=("Segoe UI", 10, "bold"), bg=self.button_color, fg=self.header_color, activebackground=self.button_hover, activeforeground=self.header_color, bd=0, padx=15, pady=8, command=self.export_report)
        report_btn.pack(side="left")
        
        # Treeview Scrollbar & Frame
        tree_frame = tk.Frame(frame, bg=self.card_color)
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Configure custom Treeview style for dark theme
        self.style.configure("Treeview", background="#1e293b", foreground="#f8fafc", fieldbackground="#1e293b", borderwidth=0, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 9, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[("selected", "#6366f1")], foreground=[("selected", "#ffffff")])
        
        columns = ("id", "host", "source", "severity", "description")
        self.findings_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")
        self.findings_tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.findings_tree.yview)
        self.findings_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Column Headings
        self.findings_tree.heading("id", text="ID")
        self.findings_tree.heading("host", text="Host / Target")
        self.findings_tree.heading("source", text="Source Tool")
        self.findings_tree.heading("severity", text="Severity")
        self.findings_tree.heading("description", text="Vulnerability / Finding")
        
        # Column Widths
        self.findings_tree.column("id", width=40, anchor="center")
        self.findings_tree.column("host", width=130, anchor="w")
        self.findings_tree.column("source", width=100, anchor="center")
        self.findings_tree.column("severity", width=100, anchor="center")
        self.findings_tree.column("description", width=400, anchor="w")
        
        self.findings_tree.bind("<<TreeviewSelect>>", self.on_finding_select)
        
        # Color Tags
        self.findings_tree.tag_configure("Critical", foreground="#f43f5e") # Red-rose
        self.findings_tree.tag_configure("High", foreground="#f97316")     # Orange
        self.findings_tree.tag_configure("Medium", foreground="#eab308")   # Yellow
        self.findings_tree.tag_configure("Low", foreground="#10b981")      # Emerald
        
        # Details Panel
        detail_header = tk.Label(frame, text="Detailed Evidence & Mitigation Remediation", font=("Segoe UI", 11, "bold"), bg=self.card_color, fg=self.header_color)
        detail_header.pack(anchor="w", pady=(10, 5))
        
        self.detail_text = tk.Text(frame, height=8, bg=self.bg_color, fg=self.header_color, font=("Consolas", 10), bd=0, highlightbackground=self.button_color, highlightthickness=1, wrap="word", state="disabled")
        self.detail_text.pack(fill="x", ipady=5)
        
    def load_findings(self):
        # Clear existing entries
        for row in self.findings_tree.get_children():
            self.findings_tree.delete(row)
            
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.configure(state="disabled")
        
        self.all_findings = []
        import re
        
        # 1. Parse Nmap XML Output
        if os.path.exists("/tmp/cracken5_nmap.xml"):
            try:
                tree = ET.parse("/tmp/cracken5_nmap.xml")
                root = tree.getroot()
                for host in root.findall("host"):
                    addr_el = host.find("address")
                    addr = addr_el.get("addr") if addr_el is not None else "Unknown Host"
                    for port in host.findall("ports/port"):
                        portid = port.get("portid")
                        protocol = port.get("protocol")
                        state_el = port.find("state")
                        state = state_el.get("state") if state_el is not None else "unknown"
                        if state == "open":
                            service = port.find("service")
                            service_name = service.get("name") if service is not None else "unknown"
                            service_prod = service.get("product") if service is not None else ""
                            service_ver = service.get("version") if service is not None else ""
                            
                            desc = f"Open Port {portid}/{protocol} running {service_name} {service_prod} {service_ver}".strip()
                            
                            # Determine Severity / Mitigation
                            sev = "Low"
                            mitigation = f"Ensure the service running on port {portid} is necessary. Implement packet-filtering firewall policies to block unsolicited incoming traffic."
                            if portid in ["21", "23"]:
                                sev = "Medium"
                                mitigation = f"Insecure plain-text authentication protocol (FTP/Telnet) running on port {portid}. Replace immediately with secure SSH or SFTP equivalents."
                            elif portid in ["3389", "445"]:
                                sev = "High"
                                mitigation = f"Sensitive service interface accessible on port {portid}. Restrict this port behind a secure network VPN and enable Multi-Factor Authentication."
                                
                            detail = f"Host Address: {addr}\nPort: {portid}/{protocol}\nState: {state}\nService Name: {service_name}\nProduct Vendor: {service_prod}\nProduct Version: {service_ver}"
                            
                            self.all_findings.append({
                                "host": addr,
                                "source": "Nmap",
                                "severity": sev,
                                "description": desc,
                                "mitigation": mitigation,
                                "detail": detail
                            })
            except Exception as e:
                print(f"Error parsing Nmap XML: {e}")
                
        # 2. Parse SQLMap Logs
        sqlmap_logs = glob.glob(os.path.expanduser("~/.local/share/sqlmap/output/*/log"))
        for log_file in sqlmap_logs:
            host = os.path.basename(os.path.dirname(log_file))
            try:
                with open(log_file, "r") as f:
                    content = f.read()
                    
                parts = content.split("---")
                for part in parts:
                    if "Parameter:" in part and "Type:" in part:
                        param_match = re.search(r"Parameter:\s+([^\n]+)", part)
                        param_name = param_match.group(1).strip() if param_match else "unknown"
                        
                        types = re.findall(r"Type:\s+([^\n]+)", part)
                        titles = re.findall(r"Title:\s+([^\n]+)", part)
                        payloads = re.findall(r"Payload:\s+([^\n]+)", part)
                        
                        for i in range(len(titles)):
                            t_type = types[i].strip() if i < len(types) else "SQL Injection"
                            t_title = titles[i].strip() if i < len(titles) else "Vulnerable parameter"
                            t_payload = payloads[i].strip() if i < len(payloads) else ""
                            
                            desc = f"SQL Injection on parameter '{param_name}' via {t_title}"
                            mitigation = "Secure the database query code using parameterized SQL queries (Prepared Statements). Never execute dynamic SQL statements containing concatenated parameters."
                            
                            detail = f"Host: {host}\nParameter Target: {param_name}\nInjection Type: {t_type}\nMethod Technique: {t_title}\nPayload String: {t_payload}"
                            
                            self.all_findings.append({
                                "host": host,
                                "source": "SQLMap",
                                "severity": "Critical",
                                "description": desc,
                                "mitigation": mitigation,
                                "detail": detail
                            })
            except Exception as e:
                print(f"Error parsing SQLMap log: {e}")
                
        # Populate Treeview
        for idx, f in enumerate(self.all_findings):
            self.findings_tree.insert("", "end", values=(idx + 1, f["host"], f["source"], f["severity"], f["description"]), tags=(f["severity"],))
            
    def on_finding_select(self, event):
        selected_items = self.findings_tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        item_values = self.findings_tree.item(selected_item, "values")
        if not item_values:
            return
            
        finding_id = int(item_values[0]) - 1
        if 0 <= finding_id < len(self.all_findings):
            f = self.all_findings[finding_id]
            
            detail_content = f"=== VULNERABILITY EVIDENCE DETAILED LOG ===\n\n"
            detail_content += f"{f['detail']}\n\n"
            detail_content += f"=== REMEDIATION & MITIGATION STEPS ===\n\n"
            detail_content += f"{f['mitigation']}\n"
            
            self.detail_text.configure(state="normal")
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("1.0", detail_content)
            self.detail_text.configure(state="disabled")
            
    def export_report(self):
        if not hasattr(self, 'all_findings') or not self.all_findings:
            messagebox.showwarning("Warning", "No findings loaded. Please load findings before exporting.")
            return
            
        # Count Severities
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for f in self.all_findings:
            if f["severity"] in counts:
                counts[f["severity"]] += 1
                
        total = len(self.all_findings)
        
        # Color classes
        colors = {
            "Critical": "#f43f5e",
            "High": "#f97316",
            "Medium": "#eab308",
            "Low": "#10b981"
        }
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cr4cKen5 Security Audit Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, sans-serif;
            background-color: #0f172a;
            color: #94a3b8;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #1e293b;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            color: #f8fafc;
            margin-top: 0;
            border-bottom: 2px solid #6366f1;
            padding-bottom: 15px;
            font-size: 28px;
        }}
        h2 {{
            color: #f8fafc;
            font-size: 20px;
            margin-top: 30px;
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
        }}
        .summary-box {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            gap: 15px;
        }}
        .metric-card {{
            flex: 1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #334155;
        }}
        .metric-val {{
            font-size: 32px;
            font-weight: bold;
            color: #f8fafc;
        }}
        .metric-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }}
        .finding-card {{
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #6366f1;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            color: #ffffff;
            margin-right: 10px;
        }}
        .meta-line {{
            margin: 10px 0;
            font-size: 13px;
        }}
        .meta-line span {{
            font-weight: bold;
            color: #f8fafc;
        }}
        .details-box {{
            background-color: #1e293b;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
            color: #e2e8f0;
            margin-top: 15px;
            border: 1px solid #334155;
            font-size: 13px;
        }}
        .remediation-box {{
            margin-top: 15px;
            padding: 15px;
            background-color: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 6px;
            font-size: 14px;
        }}
        .remediation-box strong {{
            color: #f8fafc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Cr4cKen5 Security Audit Report</h1>
        <p>This report compiles parsed scanning and auditing metrics from the Cr4cKen5 Security Suite. Ensure all recommended patching/remediation actions are reviewed.</p>
        
        <h2>Executive Summary</h2>
        <div class="summary-box">
            <div class="metric-card" style="border-top: 4px solid #f43f5e;">
                <div class="metric-val">{counts["Critical"]}</div>
                <div class="metric-label" style="color: #f43f5e;">Critical</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid #f97316;">
                <div class="metric-val">{counts["High"]}</div>
                <div class="metric-label" style="color: #f97316;">High</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid #eab308;">
                <div class="metric-val">{counts["Medium"]}</div>
                <div class="metric-label" style="color: #eab308;">Medium</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid #10b981;">
                <div class="metric-val">{counts["Low"]}</div>
                <div class="metric-label" style="color: #10b981;">Low</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid #6366f1;">
                <div class="metric-val">{total}</div>
                <div class="metric-label" style="color: #6366f1;">Total Issues</div>
            </div>
        </div>
        
        <h2>Detailed Findings</h2>
        """
        
        for f in self.all_findings:
            sev_color = colors.get(f["severity"], "#94a3b8")
            html_content += f"""
            <div class="finding-card" style="border-left-color: {sev_color};">
                <span class="badge" style="background-color: {sev_color};">{f["severity"]}</span>
                <span style="font-weight: bold; font-size: 16px; color: #f8fafc;">{f["description"]}</span>
                
                <div class="meta-line">
                    <span>Target Host:</span> {f["host"]} | <span>Source Tool:</span> {f["source"]}
                </div>
                
                <div class="details-box">{f["detail"]}</div>
                
                <div class="remediation-box">
                    <strong>Remediation Recommendation:</strong><br>
                    {f["mitigation"]}
                </div>
            </div>
            """
            
        html_content += """
    </div>
</body>
</html>
"""
        
        report_path = "/tmp/cracken5_security_report.html"
        try:
            with open(report_path, "w") as f:
                f.write(html_content)
            webbrowser.open("file://" + report_path)
            messagebox.showinfo("Success", f"Report successfully generated and opened in your browser:\n{report_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberDashboard(root)
    root.mainloop()
