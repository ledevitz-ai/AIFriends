from dotenv import load_dotenv
load_dotenv()# app.py - WhatsApp стиль с 6 друзьями
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Подключаем DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

friends_data = [
    {"id": 1, "name": "Дима", "personality": "Саркастичный айтишник", "color": "#4CAF50"},
    {"id": 2, "name": "Лена", "personality": "Эмпатичная психолог", "color": "#E91E63"},
    {"id": 3, "name": "Артём", "personality": "Спортивный мотиватор", "color": "#2196F3"},
    {"id": 4, "name": "Катя", "personality": "Творческая художница", "color": "#9C27B0"},
    {"id": 5, "name": "Миша", "personality": "Эрудированный ботаник", "color": "#FF9800"},
    {"id": 6, "name": "Аня", "personality": "Жизнерадостная блогерша", "color": "#00BCD4"}
]

class ChatRequest(BaseModel):
    message: str
    friend_id: int

@app.get("/api/friends")
async def get_friends():
    return {"friends": friends_data}

@app.post("/api/chat")
async def chat_with_friend(request: ChatRequest):
    friend = next((f for f in friends_data if f["id"] == request.friend_id), None)
    if not friend:
        return {"friend_id": request.friend_id, "response": "Друг не найден"}
    
    # Промпт с характером друга
    prompt = f"""Ты {friend['name']}, {friend['personality']}. 
Твой друг написал тебе: "{request.message}"
Ответь коротко, естественно, как в переписке в WhatsApp. Не говори что ты ИИ. Ответ в одну-две фразы."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка API: {e}")
        # Запасной вариант при ошибке
        fallback = {
            1: "Слышь, потом расскажу",
            2: "Я тебя слышу",
            3: "Погнали!",
            4: "Как красиво сказано",
            5: "Интересно...",
            6: "ОМГ! 🔥"
        }
        answer = fallback.get(request.friend_id, "Привет!")
    
    return {"friend_id": request.friend_id, "response": answer}

@app.get("/")
from fastapi.staticfiles import StaticFiles

# В самом начале, после создания app
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/manifest.json")
async def manifest():
    from fastapi.responses import JSONResponse
    import json
    with open("manifest.json", "r", encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))
async def root():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ИИ Друзья</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #e5ddd5; height: 100vh; }
            .app { display: flex; height: 100vh; }
            .sidebar { width: 300px; background: white; border-right: 1px solid #ddd; display: flex; flex-direction: column; }
            .sidebar-header { background: #075e54; padding: 20px; color: white; }
            .friends-list { flex: 1; overflow-y: auto; }
            .friend { display: flex; align-items: center; padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #eee; }
            .friend:hover { background: #f5f5f5; }
            .friend.active { background: #ebebeb; }
            .avatar { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; color: white; margin-right: 15px; flex-shrink: 0; }
            .friend-name { font-weight: bold; margin-bottom: 4px; }
            .friend-personality { font-size: 12px; color: #667781; }
            .chat { flex: 1; display: flex; flex-direction: column; background: #efeae2; }
            .chat-header { background: #f0f2f5; padding: 10px 16px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #ddd; }
            .chat-avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white; }
            .messages { flex: 1; overflow-y: auto; padding: 20px; }
            .message { display: flex; margin-bottom: 8px; }
            .message.user { justify-content: flex-end; }
            .message.friend { justify-content: flex-start; }
            .bubble { max-width: 60%; padding: 8px 12px; border-radius: 8px; font-size: 14px; }
            .message.user .bubble { background: #d9fdd3; }
            .message.friend .bubble { background: white; }
            .bubble-name { font-size: 11px; color: #667781; margin-bottom: 2px; }
            .input-area { background: #f0f2f5; padding: 10px 16px; display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 10px 15px; border: none; border-radius: 25px; outline: none; font-size: 14px; background: white; }
            .input-area input:disabled { background: #f0f2f5; }
            .input-area button { background: #075e54; border: none; width: 40px; height: 40px; border-radius: 50%; color: white; font-size: 18px; cursor: pointer; }
            .input-area button:disabled { background: #ccc; cursor: not-allowed; }
            .empty-chat { text-align: center; padding: 60px 20px; color: #667781; }
            .typing { padding: 10px 20px; color: #667781; font-size: 12px; display: flex; gap: 8px; }
            .dot { width: 6px; height: 6px; border-radius: 50%; background: #667781; animation: pulse 1.4s infinite; }
            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes pulse { 0%, 60%, 100% { opacity: 0.4; } 30% { opacity: 1; } }
        </style>
        <link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/static/icon-192.png">
<meta name="theme-color" content="#075e54">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
    <body>
        <div class="app">
            <div class="sidebar">
                <div class="sidebar-header"><h2>👥 Друзья</h2></div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            <div class="chat">
                <div class="chat-header" id="chatHeader" style="display: none;">
                    <div class="chat-avatar" id="chatAvatar">?</div>
                    <div><h3 id="chatName"></h3></div>
                </div>
                <div class="messages" id="messages">
                    <div class="empty-chat">💬<br>Выберите друга</div>
                </div>
                <div class="typing" id="typing" style="display: none;">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                    <span>печатает...</span>
                </div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Введите сообщение" disabled>
                    <button id="sendButton" disabled>➤</button>
                </div>
            </div>
        </div>
        <script>
            let friends = [];
            let currentFriendId = null;
            let isLoading = false;
            let chatHistories = {};
            
            async function loadFriends() {
                const res = await fetch('/api/friends');
                const data = await res.json();
                friends = data.friends;
                const container = document.getElementById('friendsList');
                container.innerHTML = '';
                for (const f of friends) {
                    const div = document.createElement('div');
                    div.className = 'friend';
                    div.setAttribute('data-id', f.id);
                    div.onclick = (function(id) { return function() { selectFriend(id); }; })(f.id);
                    div.innerHTML = `
                        <div class="avatar" style="background: ${f.color}">${f.name[0]}</div>
                        <div>
                            <div class="friend-name">${f.name}</div>
                            <div class="friend-personality">${f.personality}</div>
                        </div>
                    `;
                    container.appendChild(div);
                }
            }
            
            function selectFriend(id) {
                if (currentFriendId && currentFriendId !== id) {
                    saveChat();
                }
                currentFriendId = id;
                const friend = friends.find(f => f.id === id);
                
                document.querySelectorAll('.friend').forEach(el => el.classList.remove('active'));
                const activeEl = document.querySelector(`.friend[data-id="${id}"]`);
                if (activeEl) activeEl.classList.add('active');
                
                document.getElementById('chatHeader').style.display = 'flex';
                document.getElementById('chatName').innerText = friend.name;
                const av = document.getElementById('chatAvatar');
                av.innerText = friend.name[0];
                av.style.background = friend.color;
                
                const input = document.getElementById('messageInput');
                const btn = document.getElementById('sendButton');
                input.disabled = false;
                btn.disabled = false;
                input.focus();
                
                loadChat();
            }
            
            function saveChat() {
                if (!currentFriendId) return;
                const msgs = [];
                document.querySelectorAll('#messages .message').forEach(el => {
                    msgs.push({
                        role: el.classList.contains('user') ? 'user' : 'friend',
                        text: el.querySelector('.bubble').innerText
                    });
                });
                if (msgs.length) chatHistories[currentFriendId] = msgs;
            }
            
            function loadChat() {
                const container = document.getElementById('messages');
                const history = chatHistories[currentFriendId];
                if (history && history.length) {
                    container.innerHTML = '';
                    history.forEach(msg => {
                        const div = document.createElement('div');
                        div.className = `message ${msg.role}`;
                        div.innerHTML = `<div class="bubble">${msg.text}</div>`;
                        container.appendChild(div);
                    });
                } else {
                    container.innerHTML = '<div class="empty-chat">💬<br>Напишите что-нибудь</div>';
                }
                container.scrollTop = container.scrollHeight;
            }
            
            function addMessage(role, text, friendId = null) {
                const container = document.getElementById('messages');
                const empty = container.querySelector('.empty-chat');
                if (empty) empty.remove();
                
                const div = document.createElement('div');
                div.className = `message ${role}`;
                if (role === 'friend' && friendId) {
                    const friend = friends.find(f => f.id === friendId);
                    div.innerHTML = `<div class="bubble"><div class="bubble-name">${friend.name}</div>${text}</div>`;
                } else {
                    div.innerHTML = `<div class="bubble">${text}</div>`;
                }
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const msg = input.value.trim();
                if (!msg || !currentFriendId || isLoading) return;
                
                addMessage('user', msg);
                input.value = '';
                isLoading = true;
                const btn = document.getElementById('sendButton');
                const typing = document.getElementById('typing');
                btn.disabled = true;
                typing.style.display = 'flex';
                
                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: msg, friend_id: currentFriendId})
                    });
                    const data = await res.json();
                    addMessage('friend', data.response, data.friend_id);
                    saveChat();
                } catch(e) {
                    console.error(e);
                    addMessage('friend', 'Ошибка! Попробуй еще раз', currentFriendId);
                }
                isLoading = false;
                btn.disabled = false;
                typing.style.display = 'none';
                input.focus();
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = function(e) {
                if (e.key === 'Enter') sendMessage();
            };
            
            loadFriends();
        </script>
    </body>
    </html>
    ''')