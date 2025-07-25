from __future__ import annotations

import os
import requests
from datetime import datetime
from flask import send_from_directory, redirect, request
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ...image.copy_images import secure_filename
from ...cookies import get_cookies_dir
from ...errors import VersionNotFoundError
from ...constants import STATIC_URL, DOWNLOAD_URL, DIST_DIR
from ... import version

def redirect_home():
    return redirect('/chat/')

def render(filename = "chat"):
    if os.path.exists(DIST_DIR) and not request.args.get("debug"):
        path = os.path.abspath(os.path.join(os.path.dirname(DIST_DIR), (filename + ("" if "." in filename else ".html"))))
        return send_from_directory(os.path.dirname(path), os.path.basename(path))
    try:
        latest_version = version.utils.latest_version
    except VersionNotFoundError:
        latest_version = version.utils.current_version
    today = datetime.today().strftime('%Y-%m-%d')
    cache_dir = os.path.join(get_cookies_dir(), ".gui_cache")
    cache_file = os.path.join(cache_dir, f"{secure_filename(filename)}.{today}.{secure_filename(f'{version.utils.current_version}-{latest_version}')}.html")
    is_temp = False
    if not os.path.exists(cache_file):
        if os.access(cache_file, os.W_OK):
            is_temp = True
        else:
            os.makedirs(cache_dir, exist_ok=True)
        response = requests.get(f"{DOWNLOAD_URL}{filename}.html")
        if not response.ok:
            found = None
            for root, _, files in os.walk(cache_dir):
                for file in files:
                    if file.startswith(secure_filename(filename)):
                        found = os.path.abspath(root), file
                break
            if found:
                return send_from_directory(found[0], found[1])
            else:
                response.raise_for_status()
        html = response.text
        html = html.replace("../dist/", f"dist/")
        html = html.replace("\"dist/", f"\"{STATIC_URL}dist/")
        if is_temp:
            return html
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(html)
    return send_from_directory(os.path.abspath(cache_dir), os.path.basename(cache_file))

class Website:
    def __init__(self, app) -> None:
        self.app = app
        self.routes = {
            '/': {
                'function': self._index,
                'methods': ['GET', 'POST']
            },
            '/chat/': {
                'function': self._chat,
                'methods': ['GET', 'POST']
            },
            '/qrcode.html': {
                'function': self._qrcode,
                'methods': ['GET', 'POST']
            },
            '/background.html': {
                'function': self._background,
                'methods': ['GET', 'POST']
            },
            '/chat/<conversation_id>': {
                'function': self._chat,
                'methods': ['GET', 'POST']
            },
            '/media/': {
                'function': redirect_home,
                'methods': ['GET', 'POST']
            },
            '/dist/<path:name>': {
                'function': self._dist,
                'methods': ['GET']
            },
        }

    def _index(self, filename = "home"):
        return render(filename)

    def _qrcode(self, filename = "qrcode"):
        return render(filename)

    def _background(self, filename = "background"):
        return render(filename)

    def _chat(self, filename = "chat"):
        filename = "chat/index" if filename == 'chat' else secure_filename(filename)
        return render(filename)

    def _dist(self, name: str):
        return send_from_directory(os.path.abspath(DIST_DIR), name)

router = APIRouter()

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Agent Chat (Verbose)</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; }
            #log { border: 1px solid #ccc; padding: 1em; height: 300px; overflow-y: auto; background: #f9f9f9; }
            #question { width: 80%; }
            #send { padding: 0.5em 1em; }
        </style>
    </head>
    <body>
        <h2>Agent Chat (Verbose Mode)</h2>
        <div>
            <input type="text" id="question" placeholder="Ask a question..." />
            <button id="send">Send</button>
        </div>
        <div id="log"></div>
        <script>
            const log = document.getElementById('log');
            const sendBtn = document.getElementById('send');
            const questionInput = document.getElementById('question');
            function appendLog(msg) {
                log.innerHTML += msg + '<br>';
                log.scrollTop = log.scrollHeight;
            }
            sendBtn.onclick = function() {
                log.innerHTML = '';
                const question = questionInput.value;
                if (!question) return;
                const evtSource = new EventSource('/v1/agent/stream?question=' + encodeURIComponent(question));
                evtSource.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.event === 'final') {
                            appendLog('<b>Final Answer:</b> ' + data.result);
                        } else if (data.event === 'agent_action') {
                            appendLog('<pre style="color: #444; background: #eee; padding: 0.5em;">' + data.log + '</pre>');
                        } else if (data.event === 'agent_finish') {
                            appendLog('<b>Final Reasoning:</b><br><pre style="color: #444; background: #eee; padding: 0.5em;">' + data.log + '</pre>');
                        } else if (data.event === 'tool_start') {
                            appendLog('<i>Tool Start:</i> ' + data.input);
                        } else if (data.event === 'tool_end') {
                            appendLog('<i>Tool End:</i> ' + data.output);
                        } else if (data.event === 'text') {
                            appendLog('<i>Text:</i> ' + data.text);
                        } else if (data.event === 'chain_start') {
                            appendLog('<i>Chain Start</i>');
                        } else if (data.event === 'chain_end') {
                            appendLog('<i>Chain End</i>');
                        }
                    } catch (e) {
                        appendLog('Error parsing event: ' + event.data);
                    }
                };
                evtSource.onerror = function() {
                    appendLog('<span style="color:red">Stream error or closed.</span>');
                    evtSource.close();
                };
            };
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)