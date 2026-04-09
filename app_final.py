from dotenv import load_dotenv
load_dotenv()# app.py - WhatsApp стиль с 6 друзьями
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from typing import Optional, List

app = FastAPI()

# Данные друзей
friends_data = [
    {"id": 1, "name": "Дима", "personality": "Саркастичный айтишник", "color": "#4CAF50"},
    {"id": 2, "name": "Лена", "personality": "Эмпатичная психолог", "color": "#E91E63"},
    {"id": 3, "name": "Артём", "personality": "Спортивный мотиватор", "color": "#2196F3"},
    {"id": 4, "name": "Катя", "personality": "Творческая художница", "color": "#9C27B0"},
    {"id": 5, "name": "Миша", "personality": "Эрудированный ботаник", "color": "#FF9800"},
    {"id": 6, "name": "Аня", "personality": "Жизнерадостная блогерша", "color": "#00BCD4"}
]

# Ответы для каждого друга
friend_responses = {
    1: ["Слышь, норм!", "Давай потом", "Окей, понял", "Ха-ха, смешно", "Кодишь сегодня?"],
    2: ["Я тебя понимаю", "Расскажи подробнее", "Держись!", "Как ты себя чувствуешь?", "Поддерживаю тебя"],
    3: ["Погнали!", "Ты сможешь!", "Отлично!", "Вперёд, бро!", "Тренировка сегодня?"],
    4: ["Красота!", "Вдохновляюще", "Мне нравится", "Как красиво!", "Рисовала сегодня"],
    5: ["Интересный факт...", "А ты знал?", "С научной точки зрения", "Любопытно...", "Почитай про это"],
    6: ["ОМГ!", "Круто! 🔥", "Лови лайк! 👍", "Супер!", "Запили видос об этом!"]
}

class ChatRequest(BaseModel):
    message: str
    friend_id: int

@app.get("/")
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
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #e5ddd5; height: 100vh; }
            .app { display: flex; height: 100vh; max-width: 1200px; margin: 0 auto; }
            .sidebar { width: 320px; background: white; border-right: 1px solid #e9ecef; display: flex; flex-direction: column; }
            .sidebar-header { background: #075e54; padding: 20px; color: white; }
            .sidebar-header h2 { font-size: 18px; font-weight: 500; }
            .friends-list { flex: 1; overflow-y: auto; }
            .friend { display: flex; align-items: center; padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #f0f0f0; transition: background 0.2s; }
            .friend:hover { background: #f5f5f5; }
            .friend.active { background: #ebebeb; }
            .avatar { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; color: white; margin-right: 15px; flex-shrink: 0; }
            .friend-info { flex: 1; }
            .friend-name { font-weight: 600; font-size: 16px; margin-bottom: 4px; }
            .friend-personality { font-size: 12px; color: #667781; }
            .chat { flex: 1; display: flex; flex-direction: column; background: #efeae2; }
            .chat-header { background: #f0f2f5; padding: 10px 16px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #e9ecef; }
            .chat-avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white; }
            .chat-header-info h3 { font-size: 16px; font-weight: 500; }
            .messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 8px; }
            .message { display: flex; margin-bottom: 4px; }
            .message.user { justify-content: flex-end; }
            .message.friend { justify-content: flex-start; }
            .bubble { max-width: 65%; padding: 8px 12px; border-radius: 8px; font-size: 14px; line-height: 1.4; }
            .message.user .bubble { background: #d9fdd3; color: #111; border-top-right-radius: 2px; }
            .message.friend .bubble { background: white; color: #111; border-top-left-radius: 2px; }
            .bubble-name { font-size: 11px; color: #667781; margin-bottom: 2px; }
            .message-time { font-size: 10px; color: #667781; margin-left: 8px; display: inline-block; }
            .typing { padding: 10px 20px; color: #667781; font-size: 12px; display: flex; align-items: center; gap: 8px; }
            .typing-dots span { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #667781; animation: typing 1.4s infinite; }
            .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-6px); opacity: 1; } }
            .input-area { background: #f0f2f5; padding: 10px 16px; display: flex; gap: 12px; border-top: 1px solid #e9ecef; }
            .input-area input { flex: 1; padding: 10px 15px; border: none; border-radius: 25px; outline: none; font-size: 14px; background: white; }
            .input-area input:disabled { background: #f0f2f5; }
            .input-area button { background: #075e54; border: none; width: 40px; height: 40px; border-radius: 50%; color: white; font-size: 18px; cursor: pointer; transition: background 0.2s; }
            .input-area button:hover { background: #054a44; }
            .input-area button:disabled { background: #ccc; cursor: not-allowed; }
            .empty-chat { text-align: center; padding: 60px 20px; color: #667781; }
            .empty-chat span { font-size: 48px; display: block; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="app">
            <div class="sidebar">
                <div class="sidebar-header"><h2>👥 Мои друзья</h2></div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            <div class="chat">
                <div class="chat-header" id="chatHeader" style="display: none;">
                    <div class="chat-avatar" id="chatAvatar">?</div>
                    <div class="chat-header-info"><h3 id="chatName"></h3></div>
                </div>
                <div class="messages" id="messages">
                    <div class="empty-chat"><span>💬</span><p>Выберите друга, чтобы начать общение</p></div>
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
        <script>
            let friends = [];
            let currentFriendId = null;
            let isLoading = false;
            let chatHistories = {};
            
            async function loadFriends() {
                const response = await fetch('/api/friends');
                const data = await response.json();
                friends = data.friends;
                const container = document.getElementById('friendsList');
                container.innerHTML = '';
                friends.forEach(friend => {
                    const div = document.createElement('div');
                    div.className = 'friend';
                    div.setAttribute('data-id', friend.id);
                    div.onclick = () => selectFriend(friend.id);
                    div.innerHTML = `
                        <div class="avatar" style="background: ${friend.color}">${friend.name[0]}</div>
                        <div class="friend-info">
                            <div class="friend-name">${escapeHtml(friend.name)}</div>
                            <div class="friend-personality">${escapeHtml(friend.personality)}</div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            
            function selectFriend(id) {
                if (currentFriendId && currentFriendId !== id) {
                    saveCurrentChat();
                }
                currentFriendId = id;
                const friend = friends.find(f => f.id === id);
                
                document.querySelectorAll('.friend').forEach(el => el.classList.remove('active'));
                const selected = document.querySelector(`.friend[data-id="${id}"]`);
                if (selected) selected.classList.add('active');
                
                document.getElementById('chatHeader').style.display = 'flex';
                document.getElementById('chatName').textContent = friend.name;
                const avatar = document.getElementById('chatAvatar');
                avatar.textContent = friend.name[0];
                avatar.style.background = friend.color;
                
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                
                loadChatHistory(id);
                document.getElementById('messageInput').focus();
            }
            
            function saveCurrentChat() {
                if (!currentFriendId) return;
                const messagesContainer = document.getElementById('messages');
                const messages = [];
                messagesContainer.querySelectorAll('.message').forEach(el => {
                    const role = el.classList.contains('user') ? 'user' : 'friend';
                    const textEl = el.querySelector('.bubble');
                    if (textEl) {
                        let text = textEl.cloneNode(true);
                        const timeSpan = text.querySelector('.message-time');
                        if (timeSpan) timeSpan.remove();
                        const nameDiv = text.querySelector('.bubble-name');
                        if (nameDiv) nameDiv.remove();
                        messages.push({ role: role, content: text.textContent.trim() });
                    }
                });
                if (messages.length > 0) {
                    chatHistories[currentFriendId] = messages;
                }
            }
            
            function loadChatHistory(friendId) {
                const messagesContainer = document.getElementById('messages');
                const history = chatHistories[friendId];
                if (history && history.length > 0) {
                    messagesContainer.innerHTML = '';
                    history.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `message ${msg.role}`;
                        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                        if (msg.role === 'friend') {
                            const friend = friends.find(f => f.id === friendId);
                            messageDiv.innerHTML = `<div class="bubble"><div class="bubble-name">${friend ? friend.name : 'Друг'}</div>${escapeHtml(msg.content)}<span class="message-time">${time}</span></div>`;
                        } else {
                            messageDiv.innerHTML = `<div class="bubble">${escapeHtml(msg.content)}<span class="message-time">${time}</span></div>`;
                        }
                        messagesContainer.appendChild(messageDiv);
                    });
                } else {
                    messagesContainer.innerHTML = '<div class="empty-chat"><span>💬</span><p>Напишите что-нибудь другу</p></div>';
                }
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function addMessage(role, text, friendId = null) {
                const messagesContainer = document.getElementById('messages');
                const empty = messagesContainer.querySelector('.empty-chat');
                if (empty) empty.remove();
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                if (role === 'friend' && friendId) {
                    const friend = friends.find(f => f.id === friendId);
                    messageDiv.innerHTML = `<div class="bubble"><div class="bubble-name">${friend ? escapeHtml(friend.name) : 'Друг'}</div>${escapeHtml(text)}<span class="message-time">${time}</span></div>`;
                } else {
                    messageDiv.innerHTML = `<div class="bubble">${escapeHtml(text)}<span class="message-time">${time}</span></div>`;
                }
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
                input.value = '';
                isLoading = true;
                document.getElementById('sendButton').disabled = true;
                document.getElementById('typing').style.display = 'flex';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message, friend_id: currentFriendId })
                    });
                    const data = await response.json();
                    addMessage('friend', data.response, data.friend_id);
                    saveCurrentChat();
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('friend', '😅 Ошибка. Попробуй еще раз!', currentFriendId);
                } finally {
                    isLoading = false;
                    document.getElementById('sendButton').disabled = false;
                    document.getElementById('typing').style.display = 'none';
                    document.getElementById('messageInput').focus();
                }
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = (e) => e.key === 'Enter' && sendMessage();
            loadFriends();
        </script>
    </body>
    </html>
    ''')

@app.get("/api/friends")
async def get_friends():
    return {"friends": friends_data}

@app.post("/api/chat")
async def chat_with_friend(request: ChatRequest):
    friend = next((f for f in friends_data if f["id"] == request.friend_id), None)
    if not friend:
        return {"friend_id": request.friend_id, "response": "Друг не найден"}
    
    # Выбираем случайный ответ для этого друга
    responses_list = friend_responses.get(request.friend_id, ["Привет!"])
    answer = random.choice(responses_list)
    
    return {"friend_id": request.friend_id, "response": answer}