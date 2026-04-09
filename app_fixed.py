<<<<<<< HEAD
# app_fixed.py - полностью рабочий чат с 6 друзьями
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Подключаем DeepSeek (или OpenAI)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# Данные друзей прямо здесь, чтобы не было проблем с импортом
friends_data = [
    {
        "id": 1,
        "name": "Дима",
        "personality": "Саркастичный айтишник",
        "system_prompt": "Ты Дима, 25 лет, программист. У тебя саркастичный юмор, любишь мемы. Отвечай коротко и с юмором. Не говори что ты ИИ.",
        "avatar_color": "#4CAF50"
    },
    {
        "id": 2,
        "name": "Лена",
        "personality": "Эмпатичная психолог",
        "system_prompt": "Ты Лена, 24 года, учишься на психолога. Ты добрая, внимательная, любишь слушать. Отвечай мягко и поддерживающе.",
        "avatar_color": "#E91E63"
    },
    {
        "id": 3,
        "name": "Артём",
        "personality": "Спортивный мотиватор",
        "system_prompt": "Ты Артём, 26 лет, фитнес-тренер. Ты энергичный и позитивный. Отвечай бодро, с восклицаниями, мотивируй.",
        "avatar_color": "#2196F3"
    },
    {
        "id": 4,
        "name": "Катя",
        "personality": "Творческая художница",
        "system_prompt": "Ты Катя, 23 года, художница. Ты творческая и мечтательная. Отвечай образно и вдохновляюще.",
        "avatar_color": "#9C27B0"
    },
    {
        "id": 5,
        "name": "Миша",
        "personality": "Эрудированный ботаник",
        "system_prompt": "Ты Миша, 27 лет, аспирант-физик. Ты умный и любознательный. Отвечай вдумчиво, с интересными фактами.",
        "avatar_color": "#FF9800"
    },
    {
        "id": 6,
        "name": "Аня",
        "personality": "Жизнерадостная блогерша",
        "system_prompt": "Ты Аня, 22 года, блогер. Ты жизнерадостная и общительная. Отвечай быстро, с эмодзи и молодежным сленгом.",
        "avatar_color": "#00BCD4"
    }
]

class ChatRequest(BaseModel):
    message: str
    friend_id: int
    history: Optional[List[dict]] = []

@app.post("/api/chat")
async def chat_with_friend(request: ChatRequest):
    # Находим друга
    friend = None
    for f in friends_data:
        if f["id"] == request.friend_id:
            friend = f
            break
    
    if not friend:
        return {"error": "Друг не найден"}
    
    # Собираем сообщения для API
    messages = [
        {"role": "system", "content": friend["system_prompt"]}
    ]
    
    # Добавляем историю (последние 5 сообщений)
    if request.history:
        for msg in request.history[-5:]:
            messages.append(msg)
    
    # Добавляем текущее сообщение
    messages.append({"role": "user", "content": request.message})
    
    try:
        # Отправляем запрос в DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",  # Модель DeepSeek
            messages=messages,
            max_tokens=150,
            temperature=0.8
        )
        
        answer = response.choices[0].message.content
        
        return {
            "friend_id": friend["id"],
            "friend_name": friend["name"],
            "response": answer,
            "personality": friend["personality"]
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        # Возвращаем заглушку, но с информацией об ошибке
        return {
            "friend_id": friend["id"],
            "friend_name": friend["name"],
            "response": f"😅 Ошибка API: {str(e)[:100]}",
            "personality": friend["personality"]
        }

@app.get("/api/friends")
async def get_friends():
    return {"friends": friends_data}

@app.get("/")
async def root():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ИИ Друзья - Чат</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: #e5ddd5;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .app {
                width: 100%;
                max-width: 1200px;
                height: 100vh;
                background: white;
                display: flex;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }
            
            /* Список друзей */
            .friends-panel {
                width: 300px;
                background: #fff;
                border-right: 1px solid #e9ecef;
                display: flex;
                flex-direction: column;
            }
            
            .friends-header {
                background: #075e54;
                padding: 20px;
                color: white;
            }
            
            .friends-header h2 {
                font-size: 18px;
                font-weight: 500;
            }
            
            .friends-list {
                flex: 1;
                overflow-y: auto;
            }
            
            .friend-item {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.2s;
            }
            
            .friend-item:hover {
                background: #f5f5f5;
            }
            
            .friend-item.active {
                background: #ebebeb;
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
            
            /* Чат */
            .chat-panel {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: #efeae2;
            }
            
            .chat-header {
                background: #f0f2f5;
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 15px;
                border-bottom: 1px solid #e9ecef;
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
            
            .chat-header-info h3 {
                font-size: 16px;
                font-weight: 500;
            }
            
            .chat-header-info p {
                font-size: 12px;
                color: #667781;
            }
            
            .messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .message {
                display: flex;
                margin-bottom: 4px;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-bubble {
                max-width: 65%;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .message.user .message-bubble {
                background: #d9fdd3;
                color: #111;
                border-top-right-radius: 2px;
            }
            
            .message.friend .message-bubble {
                background: white;
                color: #111;
                border-top-left-radius: 2px;
            }
            
            .message-time {
                font-size: 10px;
                color: #667781;
                margin-left: 8px;
            }
            
            .typing {
                padding: 10px 20px;
                color: #667781;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
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
            
            .input-area {
                background: #f0f2f5;
                padding: 10px 16px;
                display: flex;
                gap: 12px;
                border-top: 1px solid #e9ecef;
            }
            
            .input-area input {
                flex: 1;
                padding: 10px 15px;
                border: none;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
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
                cursor: not-allowed;
            }
            
            .empty-chat {
                text-align: center;
                padding: 60px 20px;
                color: #667781;
            }
        </style>
    </head>
    <body>
        <div class="app">
            <div class="friends-panel">
                <div class="friends-header">
                    <h2>👥 Мои друзья</h2>
                </div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            
            <div class="chat-panel">
                <div class="chat-header" id="chatHeader" style="display: none;">
                    <div class="chat-avatar" id="chatAvatar">?</div>
                    <div class="chat-header-info">
                        <h3 id="chatName">Друг</h3>
                        <p id="chatStatus">онлайн</p>
                    </div>
                </div>
                
                <div class="messages" id="messages">
                    <div class="empty-chat" id="emptyChat">
                        💬<br>Выберите друга, чтобы начать общение
                    </div>
                </div>
                
                <div class="typing" id="typing" style="display: none;">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
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
            let chatHistory = [];
            let isLoading = false;
            
            async function loadFriends() {
                const response = await fetch('/api/friends');
                const data = await response.json();
                friends = data.friends;
                renderFriendsList();
            }
            
            function renderFriendsList() {
                const container = document.getElementById('friendsList');
                container.innerHTML = friends.map(friend => `
                    <div class="friend-item" onclick="selectFriend(${friend.id})">
                        <div class="friend-avatar" style="background: ${friend.avatar_color}">
                            ${friend.name[0]}
                        </div>
                        <div class="friend-info">
                            <div class="friend-name">${friend.name}</div>
                            <div class="friend-personality">${friend.personality}</div>
                        </div>
                    </div>
                `).join('');
            }
            
            function selectFriend(friendId) {
                currentFriendId = friendId;
                const friend = friends.find(f => f.id === friendId);
                
                document.getElementById('chatHeader').style.display = 'flex';
                document.getElementById('emptyChat').style.display = 'none';
                document.getElementById('chatName').textContent = friend.name;
                document.getElementById('chatAvatar').textContent = friend.name[0];
                document.getElementById('chatAvatar').style.background = friend.avatar_color;
                
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                
                chatHistory = [];
                document.getElementById('messages').innerHTML = '';
                document.getElementById('messageInput').focus();
            }
            
            function addMessage(role, text, friendId = null) {
                const messagesDiv = document.getElementById('messages');
                const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                
                const friend = friendId ? friends.find(f => f.id === friendId) : null;
                const nameHtml = role === 'friend' && friend ? `<div style="font-size: 11px; color: #667781; margin-bottom: 2px;">${friend.name}</div>` : '';
                
                messageDiv.innerHTML = `
                    <div class="message-bubble">
                        ${nameHtml}
                        ${escapeHtml(text)}
                        <span class="message-time">${time}</span>
                    </div>
                `;
                
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message || !currentFriendId || isLoading) return;
                
                addMessage('user', message);
                chatHistory.push({role: 'user', content: message});
                input.value = '';
                
                isLoading = true;
                document.getElementById('sendButton').disabled = true;
                document.getElementById('typing').style.display = 'flex';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            message: message,
                            friend_id: currentFriendId,
                            history: chatHistory.filter(m => m.role === 'user').slice(-5).map(m => ({
                                role: 'user',
                                content: m.content
                            }))
                        })
                    });
                    
                    const data = await response.json();
                    
                    addMessage('friend', data.response, data.friend_id);
                    chatHistory.push({role: 'assistant', content: data.response});
                    
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('friend', '😅 Ошибка подключения. Попробуй еще раз!', currentFriendId);
                } finally {
                    isLoading = false;
                    document.getElementById('sendButton').disabled = false;
                    document.getElementById('typing').style.display = 'none';
                    document.getElementById('messageInput').focus();
                }
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = (e) => {
                if (e.key === 'Enter') sendMessage();
            };
            
            loadFriends();
        </script>
    </body>
    </html>
    ''')
=======

>>>>>>> f26a77e3ee14c5b0306884e7b6997135d5d90fee
