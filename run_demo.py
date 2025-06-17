#!/usr/bin/env python3
"""
Simple script to run the Language Assessment Demo
"""

import subprocess
import sys
import os

def main():
    """Run the demo version of the Language Assessment app"""
    try:
        # Check if streamlit is available
        subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                      check=True, capture_output=True)
        
        # Run the demo
        print("Starting Language Assessment Demo...")
        print("Open your browser to http://localhost:8501")
        print("Press Ctrl+C to stop")
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "demo.py"])
        
    except subprocess.CalledProcessError:
        print("Error: Streamlit is not installed. Please install it with:")
        print("pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 