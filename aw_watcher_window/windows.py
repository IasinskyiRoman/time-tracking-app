from typing import Optional

import os
import time

import win32gui
import win32api
import win32process
import pywintypes

def get_app_path(hwnd) -> Optional[str]:
    """Get application path given hwnd."""
    path = None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = win32api.OpenProcess(0x0400, False, pid)
    except pywintypes.error as e:
        # Handle the error, maybe log it for debugging
        print(f"Error accessing process {pid}: {str(e)}")
        # Return None or a default value if appropriate for your logic
        return None


    try:
        path = win32process.GetModuleFileNameEx(process, 0)
    finally:
        win32api.CloseHandle(process)

    return path

def get_app_name(hwnd) -> Optional[str]:
    """Get application filename given hwnd."""
    path = get_app_path(hwnd)

    if path is None:
        return None
    
    return os.path.basename(path)

def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_active_window_handle():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd


if __name__ == "__main__":
    while True:
        hwnd = get_active_window_handle()
        print("Title:", get_window_title(hwnd))
        print("App:", get_app_name(hwnd))
        time.sleep(1.0)