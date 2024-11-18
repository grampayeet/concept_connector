from flask import Flask, request, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


@app.route('/authenticate', methods=['GET'])
def authenticate():
    try:
        # Initialize the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

        # Set the redirect URI explicitly
        redirect_uri = 'https://concept-connector.onrender.com/oauth-callback'
        flow.redirect_uri = redirect_uri

        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')

        # Provide the URL to the user
        return jsonify({
            'message': 'Go to the following URL to authorize',
            'auth_url': auth_url
        })
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/oauth-callback', methods=['GET'])
def oauth_callback():
    try:
        # Initialize the OAuth flow again
        redirect_uri = 'https://concept-connector.onrender.com/oauth-callback'
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.redirect_uri = redirect_uri

        # Retrieve the authorization response URL
        flow.fetch_token(authorization_response=request.url)

        # Save credentials to a file for future use
        creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        return jsonify({'status': 'Authentication successful', 'message': 'You can now use /list-files'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/list-files', methods=['GET'])
def list_files():
    try:
        # Load saved credentials
        if not os.path.exists('token.json'):
            return jsonify({'error': 'You must authenticate first using /authenticate'})
        
        with open('token.json', 'r') as token:
            creds_data = json.load(token)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

        # Build the Drive API service
        service = build('drive', 'v3', credentials=creds)
        folder_id = '1A9jEnpg_2YXKA37TSeE1_--7s43Ti0yF'
        results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get('files', [])

        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
