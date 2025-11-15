import argparse
import os
import sys
import threading
from typing import List

from desktop.config import load_config, save_config, DesktopConfig, CONFIG_PATH
from desktop.runner import BatchRunner
from desktop.scheduler import Scheduler


def _run_once(cfg: DesktopConfig) -> bool:
    """Run a single batch analysis."""
    runner = BatchRunner(cfg)
    return runner.run_analysis()


def cli_main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="RealFlip Desktop Batch Analyzer")
    parser.add_argument("--run-once", action="store_true", help="Run a single batch now and exit")
    parser.add_argument("--show-config-path", action="store_true", help="Print the config file path and exit")
    
    # Check for help first
    if "--help" in argv or "-h" in argv:
        parser.print_help()
        return 0
    
    # Parse args
    args = parser.parse_args(argv)

    if args.show_config_path:
        print(CONFIG_PATH)
        return 0

    if args.run_once:
        cfg = load_config()
        success = _run_once(cfg)
        return 0 if success else 1

    # Minimal settings UI using Tkinter (only for schedule & paths)
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("RealFlip Batch Analyzer")

    scheduler = Scheduler()

    def select_csv():
        paths = filedialog.askopenfilenames(title="Select CSV files", filetypes=[("CSV Files", "*.csv")])
        if paths:
            cfg.csv_paths = list(paths)
            save_config(cfg)
            csv_var.set("; ".join(cfg.csv_paths))

    def select_output():
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            cfg.output_dir = path
            save_config(cfg)
            out_var.set(cfg.output_dir)

    def on_schedule_change():
        try:
            minutes = int(minutes_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Minutes must be a number")
            return
        cfg.schedule.mode = "interval"
        cfg.schedule.minutes = max(1, minutes)
        save_config(cfg)
        scheduler.schedule_interval(cfg.schedule.minutes, lambda: _run_once(cfg))
        messagebox.showinfo("Scheduled", f"Batch set to run every {cfg.schedule.minutes} minutes")

    def on_run_now():
        def worker():
            try:
                _run_once(cfg)
                messagebox.showinfo("Completed", "Batch run finished. Check output folder for artifacts.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        threading.Thread(target=worker, daemon=True).start()

    # Layout
    frm = tk.Frame(root, padx=10, pady=10)
    frm.pack(fill="both", expand=True)

    tk.Label(frm, text="CSV Files:").grid(row=0, column=0, sticky="w")
    csv_var = tk.StringVar(value="; ".join(cfg.csv_paths))
    tk.Entry(frm, textvariable=csv_var, width=60).grid(row=0, column=1, sticky="we")
    tk.Button(frm, text="Browse", command=select_csv).grid(row=0, column=2)

    tk.Label(frm, text="Output Folder:").grid(row=1, column=0, sticky="w")
    out_var = tk.StringVar(value=cfg.output_dir)
    tk.Entry(frm, textvariable=out_var, width=60).grid(row=1, column=1, sticky="we")
    tk.Button(frm, text="Browse", command=select_output).grid(row=1, column=2)

    tk.Label(frm, text="Interval (minutes):").grid(row=2, column=0, sticky="w")
    minutes_var = tk.StringVar(value=str(cfg.schedule.minutes))
    tk.Entry(frm, textvariable=minutes_var, width=10).grid(row=2, column=1, sticky="w")
    tk.Button(frm, text="Apply", command=on_schedule_change).grid(row=2, column=2)

    tk.Button(frm, text="Run Now", command=on_run_now).grid(row=3, column=1, pady=10, sticky="e")

    # Start scheduler
    scheduler.start()
    scheduler.schedule_interval(cfg.schedule.minutes, lambda: _run_once(cfg))

    root.mainloop()
    scheduler.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main(sys.argv[1:]))


