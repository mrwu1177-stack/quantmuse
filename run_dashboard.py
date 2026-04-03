#!/usr/bin/env python3
"""
Trading System Dashboard Launcher
Run this script to start the Streamlit dashboard
"""

import subprocess
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """Launch the Streamlit dashboard"""
    print("🚀 Starting Trading System Dashboard...")
    print("📊 Dashboard will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "data_service", "dashboard", "dashboard_app.py")
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Make sure you have installed the required dependencies:")
        print("   pip install -e .[ai,visualization]")

if __name__ == "__main__":
    main() 