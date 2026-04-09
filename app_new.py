from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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

@app.post("/api/chat")
async def chat_with_friend(request: ChatRequest):
    friend = next((f for f in friends_data if f["id"] == request.friend_id), None)
    if not friend:
        return {"response": "Друг не найден"}
    
    prompt = f"Ты {friend['name']}, {friend['personality']}. Ответь другу на сообщение: {request.message}. Ответь коротко."
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return {"friend_id": friend["id"], "response": response.choices[0].message.content}
    except:
        return {"friend_id": friend["id"], "response": "Привет! Как дела?"}

@app.get("/api/friends")
async def get_friends():
    return {"friends": friends_data}

@app.get("/")
async def root():
    return HTMLResponse("""
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
            .sidebar { width: 300px; background: white; border-right: 1px solid #ddd; }
            .sidebar-header { background: #075e54; padding: 20px; color: white; }
            .friends-list { overflow-y: auto; }
            .friend { display: flex; align-items: center; padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #eee; }
            .friend:hover { background: #f5f5f5; }
            .friend.active { background: #ebebeb; }
            .avatar { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; color: white; margin-right: 15px; }
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
            .input-area { background: #f0f2f5; padding: 10px 16px; display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 10px 15px; border: none; border-radius: 25px; outline: none; }
            .input-area button { background: #075e54; border: none; width: 40px; height: 40px; border-radius: 50%; color: white; font-size: 18px; cursor: pointer; }
            .empty { text-align: center; padding: 60px 20px; color: #667781; }
            .typing { padding: 10px 20px; color: #667781; font-size: 12px; display: flex; gap: 8px; }
            .dot { width: 6px; height: 6px; border-radius: 50%; background: #667781; animation: pulse 1.4s infinite; }
            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes pulse { 0%, 60%, 100% { opacity: 0.4; } 30% { opacity: 1; } }
        </style>
    </head>
    <body>
        <div class="app">
            <div class="sidebar">
                <div class="sidebar-header"><h2>👥 Друзья</h2></div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            <div class="chat">
                <div class="chat-header" id="chatHeader" style="display:none">
                    <div class="chat-avatar" id="chatAvatar">?</div>
                    <h3 id="chatName"></h3>
                </div>
                <div class="messages" id="messages">
                    <div class="empty">💬<br>Выберите друга</div>
                </div>
                <div class="typing" id="typing" style="display:none">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                    <span>печатает...</span>
                </div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Сообщение" disabled>
                    <button id="sendButton" disabled>➤</button>
                </div>
            </div>
        </div>
        <script>
            let friends = [], currentId = null, loading = false, histories = {};
            
            document.getElementById('friendsList').onclick = (e) => {
                const item = e.target.closest('.friend');
                if (item) selectFriend(parseInt(item.dataset.id));
            };
            
            async function loadFriends() {
                const res = await fetch('/api/friends');
                const data = await res.json();
                friends = data.friends;
                const container = document.getElementById('friendsList');
                container.innerHTML = friends.map(f => `
                    <div class="friend" data-id="${f.id}">
                        <div class="avatar" style="background:${f.color}">${f.name[0]}</div>
                        <div><b>${f.name}</b><br><small>${f.personality}</small></div>
                    </div>
                `).join('');
            }
            
            function selectFriend(id) {
                if (currentId && currentId !== id) saveChat();
                currentId = id;
                const friend = friends.find(f => f.id === id);
                
                document.querySelectorAll('.friend').forEach(el => el.classList.remove('active'));
                document.querySelector(`.friend[data-id="${id}"]`).classList.add('active');
                
                document.getElementById('chatHeader').style.display = 'flex';
                document.getElementById('chatName').innerText = friend.name;
                const av = document.getElementById('chatAvatar');
                av.innerText = friend.name[0];
                av.style.background = friend.color;
                
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                
                loadChat();
            }
            
            function saveChat() {
                if (!currentId) return;
                const msgs = [];
                document.querySelectorAll('#messages .message').forEach(el => {
                    msgs.push({
                        role: el.classList.contains('user') ? 'user' : 'friend',
                        text: el.querySelector('.bubble').innerText
                    });
                });
                if (msgs.length) histories[currentId] = msgs;
            }
            
            function loadChat() {
                const container = document.getElementById('messages');
                const history = histories[currentId];
                if (history && history.length) {
                    container.innerHTML = history.map(msg => `
                        <div class="message ${msg.role}">
                            <div class="bubble">${msg.text}</div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div class="empty">💬<br>Напишите что-нибудь</div>';
                }
                container.scrollTop = container.scrollHeight;
            }
            
            function addMessage(role, text) {
                const container = document.getElementById('messages');
                const empty = container.querySelector('.empty');
                if (empty) empty.remove();
                const div = document.createElement('div');
                div.className = `message ${role}`;
                div.innerHTML = `<div class="bubble">${text}</div>`;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const msg = input.value.trim();
                if (!msg || !currentId || loading) return;
                
                addMessage('user', msg);
                input.value = '';
                loading = true;
                document.getElementById('sendButton').disabled = true;
                document.getElementById('typing').style.display = 'flex';
                
                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: msg, friend_id: currentId})
                    });
                    const data = await res.json();
                    addMessage('friend', data.response);
                    saveChat();
                } catch(e) {
                    addMessage('friend', 'Ошибка! Попробуй еще раз');
                }
                loading = false;
                document.getElementById('sendButton').disabled = false;
                document.getElementById('typing').style.display = 'none';
                input.focus();
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = (e) => e.key === 'Enter' && sendMessage();
            loadFriends();
        </script>
    </body>
    </html>
    """)