from fastapi import FastAPI, HTTPException
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

# Данные друзей
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
    friend = None
    for f in friends_data:
        if f["id"] == request.friend_id:
            friend = f
            break
    
    if not friend:
        return {"friend_id": request.friend_id, "response": "Друг не найден"}
    
    prompt = f"Ты {friend['name']}, {friend['personality']}. Твой друг написал: '{request.message}'. Ответь коротко, как в WhatsApp."
    
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
async def root():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ИИ Друзья</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
        <meta name="theme-color" content="#075e54">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: #075e54;
                height: 100vh;
                overflow: hidden;
            }
            
            /* Основной контейнер */
            .app {
                height: 100vh;
                background: #fff;
                position: relative;
            }
            
            /* Экраны */
            .screen {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                transition: transform 0.3s ease;
                background: #fff;
            }
            
            .screen.friends-screen {
                transform: translateX(0);
                z-index: 1;
            }
            
            .screen.chat-screen {
                transform: translateX(100%);
                z-index: 2;
            }
            
            .screen.chat-screen.active {
                transform: translateX(0);
            }
            
            .screen.friends-screen.hide {
                transform: translateX(-100%);
            }
            
            /* Шапка списка друзей */
            .friends-header {
                background: #075e54;
                padding: 20px 16px;
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
                height: 60px;
            }
            
            .friends-header h1 {
                font-size: 20px;
                font-weight: 500;
            }
            
            /* Список друзей */
            .friends-list {
                overflow-y: auto;
                height: calc(100% - 60px);
                background: #fff;
            }
            
            .friend-item {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.2s;
            }
            
            .friend-item:active {
                background: #f5f5f5;
            }
            
            .friend-avatar {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-right: 15px;
                flex-shrink: 0;
            }
            
            .friend-info {
                flex: 1;
            }
            
            .friend-name {
                font-weight: 600;
                font-size: 16px;
                margin-bottom: 4px;
            }
            
            .friend-personality {
                font-size: 12px;
                color: #667781;
            }
            
            /* Шапка чата */
            .chat-header {
                background: #075e54;
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 15px;
                height: 60px;
                color: white;
            }
            
            .back-button {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .chat-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
            
            .chat-header-info {
                flex: 1;
            }
            
            .chat-header-info h3 {
                font-size: 16px;
                font-weight: 500;
            }
            
            .chat-header-info p {
                font-size: 12px;
                opacity: 0.9;
            }
            
            /* Область сообщений */
            .messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #efeae2;
                height: calc(100% - 120px);
            }
            
            .message {
                display: flex;
                margin-bottom: 8px;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.friend {
                justify-content: flex-start;
            }
            
            .bubble {
                max-width: 70%;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .message.user .bubble {
                background: #d9fdd3;
                color: #111;
                border-top-right-radius: 2px;
            }
            
            .message.friend .bubble {
                background: white;
                color: #111;
                border-top-left-radius: 2px;
            }
            
            .bubble-name {
                font-size: 11px;
                color: #667781;
                margin-bottom: 2px;
            }
            
            /* Панель ввода */
            .input-area {
                background: #f0f2f5;
                padding: 10px 16px;
                display: flex;
                gap: 12px;
                border-top: 1px solid #e9ecef;
                height: 60px;
            }
            
            .input-area input {
                flex: 1;
                padding: 10px 15px;
                border: none;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
                background: white;
            }
            
            .input-area input:disabled {
                background: #f0f2f5;
            }
            
            .input-area button {
                background: #075e54;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                color: white;
                font-size: 18px;
                cursor: pointer;
            }
            
            .input-area button:disabled {
                background: #ccc;
            }
            
            /* Индикатор печати */
            .typing {
                padding: 10px 20px;
                color: #667781;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                background: #efeae2;
            }
            
            .typing-dots span {
                display: inline-block;
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #667781;
                animation: typing 1.4s infinite;
            }
            
            .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                30% { transform: translateY(-6px); opacity: 1; }
            }
            
            .chat-container {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
        </style>
    </head>
    <body>
        <div class="app">
            <!-- Экран списка друзей -->
            <div class="screen friends-screen" id="friendsScreen">
                <div class="friends-header">
                    <h1>👥 Чаты</h1>
                </div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            
            <!-- Экран чата -->
            <div class="screen chat-screen" id="chatScreen">
                <div class="chat-container">
                    <div class="chat-header">
                        <button class="back-button" id="backButton">←</button>
                        <div class="chat-avatar" id="chatAvatar">?</div>
                        <div class="chat-header-info">
                            <h3 id="chatName">Друг</h3>
                            <p id="chatStatus">онлайн</p>
                        </div>
                    </div>
                    
                    <div class="messages" id="messages">
                        <div style="text-align: center; padding: 40px; color: #667781;">
                            💬<br>Напишите что-нибудь
                        </div>
                    </div>
                    
                    <div class="typing" id="typing" style="display: none;">
                        <div class="typing-dots"><span></span><span></span><span></span></div>
                        <span>печатает...</span>
                    </div>
                    
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Введите сообщение" disabled>
                        <button id="sendButton" disabled>➤</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let friends = [];
            let currentFriendId = null;
            let isLoading = false;
            let chatHistories = {};
            
            // Навигация
            function showFriendsScreen() {
                document.getElementById('friendsScreen').classList.remove('hide');
                document.getElementById('chatScreen').classList.remove('active');
                document.getElementById('chatScreen').style.transform = 'translateX(100%)';
            }
            
            function showChatScreen() {
                document.getElementById('friendsScreen').classList.add('hide');
                document.getElementById('chatScreen').classList.add('active');
                document.getElementById('chatScreen').style.transform = 'translateX(0)';
            }
            
            async function loadFriends() {
                const res = await fetch('/api/friends');
                const data = await res.json();
                friends = data.friends;
                const container = document.getElementById('friendsList');
                container.innerHTML = '';
                friends.forEach(f => {
                    const div = document.createElement('div');
                    div.className = 'friend-item';
                    div.onclick = () => selectFriend(f.id);
                    div.innerHTML = `
                        <div class="friend-avatar" style="background: ${f.color}">${f.name[0]}</div>
                        <div class="friend-info">
                            <div class="friend-name">${escapeHtml(f.name)}</div>
                            <div class="friend-personality">${escapeHtml(f.personality)}</div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function selectFriend(id) {
                if (currentFriendId && currentFriendId !== id) {
                    saveChat();
                }
                currentFriendId = id;
                const friend = friends.find(f => f.id === id);
                
                // Обновляем шапку чата
                document.getElementById('chatName').innerText = friend.name;
                const avatar = document.getElementById('chatAvatar');
                avatar.innerText = friend.name[0];
                avatar.style.background = friend.color;
                
                // Активируем поле ввода
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                
                // Загружаем историю
                loadChat();
                
                // Показываем экран чата
                showChatScreen();
                
                // Фокус на поле ввода
                setTimeout(() => {
                    document.getElementById('messageInput').focus();
                }, 300);
            }
            
            function saveChat() {
                if (!currentFriendId) return;
                const container = document.getElementById('messages');
                const msgs = [];
                container.querySelectorAll('.message').forEach(el => {
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
                    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #667781;">💬<br>Напишите что-нибудь</div>';
                }
                container.scrollTop = container.scrollHeight;
            }
            
            function addMessage(role, text, friendId = null) {
                const container = document.getElementById('messages');
                const empty = container.querySelector('div[style*="text-align: center"]');
                if (empty) empty.remove();
                
                const div = document.createElement('div');
                div.className = `message ${role}`;
                if (role === 'friend' && friendId) {
                    const friend = friends.find(f => f.id === friendId);
                    div.innerHTML = `<div class="bubble"><div style="font-size:11px;color:#667781">${friend.name}</div>${escapeHtml(text)}</div>`;
                } else {
                    div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
                }
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const msg = input.value.trim();
                if (!msg || !currentFriendId || isLoading) return;
                
                addMessage('user', msg);
                input.value = '';
                isLoading = true;
                document.getElementById('sendButton').disabled = true;
                document.getElementById('typing').style.display = 'flex';
                
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
                document.getElementById('sendButton').disabled = false;
                document.getElementById('typing').style.display = 'none';
                input.focus();
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = (e) => e.key === 'Enter' && sendMessage();
            document.getElementById('backButton').onclick = showFriendsScreen;
            
            loadFriends();
        </script>
    </body>
    </html>
    ''')
