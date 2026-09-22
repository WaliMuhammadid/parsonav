import os
import requests
import sys
import traceback
import json

def run_test():
    url = 'http://localhost:5000/api/presentation-rewriter/submit'
    sample_file = 'test_sample.pptx'
    if not os.path.exists(sample_file):
        print(f"[SKIP] '{sample_file}' not found. Skipping manual sample test.")
        return
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
            data = {'mode': 'professional', 'tone': 'professional'}
            resp = requests.post(url, files=files, data=data, timeout=300)
            print('STATUS:', resp.status_code)
            try:
                print('RESPONSE:', json.dumps(resp.json(), indent=2)[:3000])
            except Exception:
                print('RESPONSE:', resp.text[:2000])
    except Exception as e:
        traceback.print_exc()
        print('ERROR:', str(e))

if __name__ == '__main__':
    run_test()
