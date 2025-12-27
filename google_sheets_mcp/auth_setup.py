import os.path
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes we need
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations'
]

def main():
    # Allow user to specify a tag, e.g., "python auth_setup.py work"
    if len(sys.argv) > 1:
        tag = sys.argv[1]
    else:
        tag = "default"
        
    output_file = f"token_{tag}.json"
    print(f"Starting authentication flow for '{tag}' account...")
    print(f"Output will be saved to: {output_file}")
    
    # Check for the secret file
    secret_file = 'client_secret.json'
    if not os.path.exists(secret_file):
        print(f"ERROR: {secret_file} not found!")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)
        # Run local server to listen for the auth callback
        creds = flow.run_local_server(port=0)
        
        # Save the tokens
        with open(output_file, 'w') as token:
            token.write(creds.to_json())
            
        print(f"\nSUCCESS! Authentication complete for {tag}.")
        print(f"'{output_file}' has been created.")
        
    except Exception as e:
        print(f"\nERROR: Authentication failed: {e}")

if __name__ == "__main__":
    main()
