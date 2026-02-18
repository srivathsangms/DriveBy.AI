from detection import DriverMonitor
import sys
import cv2
def main():
    print("Starting DriveBy.AI Engine...")
    try:
        monitor = DriverMonitor()
        
        if len(sys.argv) > 2:
            email = sys.argv[1]
            password = sys.argv[2]
            monitor.login(email, password)
        else:
            print("No credentials provided. Running in offline/demo mode (logs won't upload).")
            print("Usage: python main.py <email> <password>")
            
        monitor.run()
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
