import sqlite3

import os

import json

import urllib.request

from urllib.error import HTTPError

import time

conn = sqlite3.connect('../librarypro.db')

conn.row_factory = sqlite3.Row

cur = conn.cursor()

cur.execute('SELECT id, title, author FROM books LIMIT 5')

books = cur.fetchall()

api_key = os.environ.get('GEMINI_API_KEY')

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'

headers = {'Content-Type': 'application/json'}

prompt = 'Provide a short, 1 or 2 sentence engaging description for each of the following books based on their title and author. Return ONLY a valid JSON dictionary where the keys are the book IDs (as strings) and the values are the generated descriptions. DO NOT wrap the JSON in markdown blocks like ```json ... ```. Just return raw JSON.\n'

for b in books:

    prompt += f"ID: {b['id']}, Title: '{b['title']}', Author: {b['author']}\n"

payload = {'contents': [{'parts': [{'text': prompt}]}]}

try:

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

    with urllib.request.urlopen(req, timeout=30) as response:

        print(response.read().decode('utf-8'))

except HTTPError as e:

    print(f'HTTP Error {e.code}: {e.read().decode("utf-8")}')

except Exception as e:

    print(f'API error: {e}')

conn.close()

