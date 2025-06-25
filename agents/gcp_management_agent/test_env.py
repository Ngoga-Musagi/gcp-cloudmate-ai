import os
from dotenv import load_dotenv

load_dotenv()

print("Testing environment variables:")
print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if creds_path:
    print(f"Credentials file exists: {os.path.exists(creds_path)}")
else:
    print("No credentials path found")