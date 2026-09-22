import urllib.request, json, os

from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}'

history = [

    {'role': 'user', 'parts': [{'text': 'Hello'}]},

    {'role': 'model', 'parts': [{'text': 'Hi'}]},

    {'role': 'user', 'parts': [{'text': 'Yes'}]}

]

system_prompt = 'You are a library assistant.'

history[0]['parts'][0]['text'] = f"{system_prompt}\n\nUser: {history[0]['parts'][0]['text']}"

payload = {'contents': history}

headers = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method='POST')

try:

    with urllib.request.urlopen(req) as response:

        print(response.read().decode())

except urllib.error.HTTPError as e:

    print('HTTPError:', e.code, e.read().decode())

