"""Main entry point for StrmConvert application."""
import sys
import signal
import atexit
from app import app, config_manager, monitor


def cleanup():
    """Cleanup function to stop all monitoring on exit."""
    try:
        print("Stopping all monitoring...")
        monitor.stop_all()
        print("Cleanup complete.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        # Continue anyway to allow shutdown


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\nShutdown signal received...")
    cleanup()
    sys.exit(0)


def main():
    """Main entry point."""
    # Register cleanup handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    # Load configuration
    try:
        config = config_manager.load()
        print(f"Loaded configuration with {len(config.get('records', []))} record(s)")
    except Exception as e:
        print(f"Warning: Failed to load configuration: {e}")
        print("Starting with empty configuration.")
    
    # Start Flask application
    print("Starting StrmConvert web server on http://0.0.0.0:9115")
    print("Access the web UI to configure and control the application.")
    
    try:
        app.run(host='0.0.0.0', port=9115, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == '__main__':
    main()

