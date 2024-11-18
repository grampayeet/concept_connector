from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@app.route('/authenticate', methods=['GET'])
def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return jsonify({'status': 'authenticated'})

@app.route('/list-files', methods=['GET'])
def list_files():
    folder_id = '1A9jEnpg_2YXKA37TSeE1_--7s43Ti0yF'
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    return jsonify(results.get('files', []))

if __name__ == '__main__':
    app.run(debug=True)

