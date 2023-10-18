import requests
import json

url = "http://localhost:8000/agents/creator/stream"

payload = json.dumps({
   "model": "open_creator_agent",
   "messages": [
      {
         "role": "user",
         "content": "你能帮我做什么，写1个简单示例说明"
      }
   ]
})
headers = {
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json',
   'Accept': '*/*',
   'Host': 'localhost:8000',
   'Connection': 'keep-alive'
}

response = requests.request("POST", url, headers=headers, data=payload)
for line in response.iter_lines():
    if line:  # filter out keep-alive new lines
        print(line.decode("utf-8"))
        print("-----------------")
