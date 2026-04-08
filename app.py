# app.py - WhatsApp стиль с 6 друзьями
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
import os
from friends import friends_data, get_friend_by_id

app = FastAPI(title="Chat with AI Friends")
client = OpenAI(api_key="ваш_ключ_сюда")

class ChatRequest(BaseModel):
    message: str
    friend_id: int
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    friend_id: int
    friend_name: str
    response: str
    personality: str

@app.post("/api/chat")
async def chat_with_friend(request: ChatRequest):
    friend = get_friend_by_id(request.friend_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    messages = [{"role": "system", "content": friend["system_prompt"]}]
    
    for msg in request.history[-10:]:
        messages.append(msg)
    
    messages.append({"role": "user", "content": request.message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.8
        )
        
        return ChatResponse(
            friend_id=friend["id"],
            friend_name=friend["name"],
            response=response.choices[0].message.content,
            personality=friend["personality"]
        )
    except Exception as e:
        print(f"Error: {e}")
        return ChatResponse(
            friend_id=friend["id"],
            friend_name=friend["name"],
            response="Извини, ошибка. Попробуй еще раз!",
            personality=friend["personality"]
        )

@app.get("/api/friends")
async def get_friends():
    return {"friends": friends_data}

@app.get("/")
async def root():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp AI Friends</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
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
                overflow: hidden;
            }
            
            .whatsapp-container {
                display: flex;
                height: 100vh;
                max-width: 1400px;
                margin: 0 auto;
                background: #fff;
            }
            
            .chats-sidebar {
                width: 350px;
                background: #fff;
                border-right: 1px solid #e9ecef;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            
            .chats-header {
                background: #075e54;
                padding: 20px 16px;
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .chats-header h1 {
                font-size: 20px;
                font-weight: 500;
            }
            
            .header-icons {
                display: flex;
                gap: 20px;
            }
            
            .header-icons span {
                font-size: 20px;
                cursor: pointer;
                opacity: 0.9;
            }
            
            .search-bar {
                background: #f6f6f6;
                padding: 8px 12px;
            }
            
            .search-box {
                background: white;
                border-radius: 20px;
                padding: 8px 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .search-box span {
                color: #919191;
                font-size: 16px;
            }
            
            .search-box input {
                border: none;
                outline: none;
                flex: 1;
                font-size: 14px;
                background: transparent;
            }
            
            .friends-list {
                flex: 1;
                overflow-y: auto;
                background: #fff;
            }
            
            .friend-chat {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                cursor: pointer;
                transition: background 0.2s;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .friend-chat:hover {
                background: #f5f5f5;
            }
            
            .friend-chat.active {
                background: #ebebeb;
            }
            
            .avatar {
                width: 49px;
                height: 49px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
                font-weight: 600;
                color: white;
                margin-right: 15px;
                flex-shrink: 0;
            }
            
            .chat-info {
                flex: 1;
                min-width: 0;
            }
            
            .chat-name {
                font-size: 16px;
                font-weight: 500;
                color: #111;
                margin-bottom: 4px;
            }
            
            .chat-preview {
                font-size: 13px;
                color: #667781;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .chat-main {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: #efeae2;
                position: relative;
            }
            
            .chat-main-header {
                background: #f0f2f5;
                padding: 10px 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid #e9ecef;
                height: 60px;
            }
            
            .current-chat-info {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .back-button {
                display: none;
                cursor: pointer;
                font-size: 24px;
            }
            
            .current-avatar-small {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }
            
            .current-chat-details h3 {
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 2px;
            }
            
            .current-chat-details p {
                font-size: 12px;
                color: #667781;
            }
            
            .chat-actions {
                display: flex;
                gap: 20px;
            }
            
            .chat-actions span {
                font-size: 20px;
                cursor: pointer;
                color: #54656f;
            }
            
            .messages-area {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23efeae2"/><circle cx="10" cy="10" r="2" fill="%23d1d7db"/><circle cx="30" cy="20" r="1.5" fill="%23d1d7db"/><circle cx="50" cy="15" r="2" fill="%23d1d7db"/><circle cx="70" cy="25" r="1.5" fill="%23d1d7db"/><circle cx="20" cy="40" r="1.5" fill="%23d1d7db"/><circle cx="45" cy="45" r="2" fill="%23d1d7db"/><circle cx="80" cy="50" r="1.5" fill="%23d1d7db"/></svg>');
                background-repeat: repeat;
                display: flex;
                flex-direction: column;
            }
            
            .message-wrapper {
                display: flex;
                margin-bottom: 8px;
                width: 100%;
            }
            
            .message-wrapper.user {
                justify-content: flex-end;
            }
            
            .message-wrapper.friend {
                justify-content: flex-start;
            }
            
            .message-bubble {
                max-width: 65%;
                padding: 8px 12px;
                border-radius: 8px;
                position: relative;
                word-wrap: break-word;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .message-wrapper.user .message-bubble {
                background: #d9fdd3;
                color: #111;
                border-top-right-radius: 2px;
            }
            
            .message-wrapper.friend .message-bubble {
                background: white;
                color: #111;
                border-top-left-radius: 2px;
            }
            
            .message-time {
                font-size: 10px;
                color: #667781;
                margin-left: 8px;
                display: inline-block;
            }
            
            .message-status {
                font-size: 12px;
                margin-left: 4px;
            }
            
            .typing-indicator-wa {
                padding: 10px 20px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .typing-dots {
                display: flex;
                gap: 4px;
                align-items: center;
            }
            
            .typing-dots span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #667781;
                animation: typing 1.4s infinite;
            }
            
            .typing-dots span:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .typing-dots span:nth-child(3) {
                animation-delay: 0.4s;
            }
            
            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.4;
                }
                30% {
                    transform: translateY(-8px);
                    opacity: 1;
                }
            }
            
            .input-panel {
                background: #f0f2f5;
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                border-top: 1px solid #e9ecef;
            }
            
            .input-icons {
                display: flex;
                gap: 15px;
                color: #54656f;
            }
            
            .input-icons span {
                font-size: 22px;
                cursor: pointer;
            }
            
            .input-panel input {
                flex: 1;
                padding: 10px 15px;
                border: none;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
                background: white;
            }
            
            .input-panel input:disabled {
                background: #f0f2f5;
                cursor: not-allowed;
            }
            
            .send-button {
                background: #075e54;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background 0.2s;
            }
            
            .send-button:hover {
                background: #054a44;
            }
            
            .send-button span {
                color: white;
                font-size: 20px;
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .empty-chat {
                text-align: center;
                padding: 60px 20px;
                color: #667781;
            }
            
            .empty-chat span {
                font-size: 48px;
                margin-bottom: 20px;
                display: block;
            }
            
            @media (max-width: 768px) {
                .chats-sidebar {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                    z-index: 10;
                    transition: transform 0.3s;
                }
                
                .chats-sidebar.hide {
                    transform: translateX(-100%);
                }
                
                .back-button {
                    display: block;
                }
                
                .message-bubble {
                    max-width: 85%;
                }
            }
        </style>
    </head>
    <body>
        <div class="whatsapp-container">
            <div class="chats-sidebar" id="chatsSidebar">
                <div class="chats-header">
                    <h1>WhatsApp AI</h1>
                    <div class="header-icons">
                        <span>👥</span>
                        <span>⋮</span>
                    </div>
                </div>
                <div class="search-bar">
                    <div class="search-box">
                        <span>🔍</span>
                        <input type="text" placeholder="Поиск" id="searchInput">
                    </div>
                </div>
                <div class="friends-list" id="friendsList"></div>
            </div>
            
            <div class="chat-main" id="chatMain">
                <div class="chat-main-header">
                    <div class="current-chat-info">
                        <div class="back-button" id="backButton">←</div>
                        <div class="current-avatar-small" id="currentAvatarSmall">?</div>
                        <div class="current-chat-details">
                            <h3 id="currentFriendName">Выберите чат</h3>
                            <p id="currentStatus">онлайн</p>
                        </div>
                    </div>
                    <div class="chat-actions">
                        <span>📞</span>
                        <span>📹</span>
                        <span>⋮</span>
                    </div>
                </div>
                
                <div class="messages-area" id="messagesArea">
                    <div class="empty-chat">
                        <span>💬</span>
                        <p>Выберите друга, чтобы начать общение</p>
                    </div>
                </div>
                
                <div class="typing-indicator-wa" id="typingIndicator" style="display: none;">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span style="color: #667781; font-size: 12px;">печатает...</span>
                </div>
                
                <div class="input-panel">
                    <div class="input-icons">
                        <span>😊</span>
                        <span>📎</span>
                    </div>
                    <input type="text" id="messageInput" placeholder="Введите сообщение" disabled>
                    <button class="send-button" id="sendButton" disabled>
                        <span>➤</span>
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            let friends = [];
            let currentFriendId = null;
            let chatHistory = [];
            let isWaiting = false;
            
            async function loadFriends() {
                const response = await fetch('/api/friends');
                const data = await response.json();
                friends = data.friends;
                renderFriendsList();
            }
            
            document.getElementById('searchInput').addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const filtered = friends.filter(f => 
                    f.name.toLowerCase().includes(searchTerm) ||
                    f.personality.toLowerCase().includes(searchTerm)
                );
                renderFriendsList(filtered);
            });
            
            function renderFriendsList(filteredFriends = null) {
                const list = filteredFriends || friends;
                const container = document.getElementById('friendsList');
                
                if (list.length === 0) {
                    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #667781;">Ничего не найдено</div>';
                    return;
                }
                
                container.innerHTML = list.map(friend => `
                    <div class="friend-chat" onclick="selectFriend(${friend.id})">
                        <div class="avatar" style="background: ${friend.avatar_color}">
                            ${friend.name[0]}
                        </div>
                        <div class="chat-info">
                            <div class="chat-name">${friend.name}</div>
                            <div class="chat-preview">${friend.personality}</div>
                        </div>
                        <div class="chat-time"></div>
                    </div>
                `).join('');
            }
            
            function selectFriend(friendId) {
                currentFriendId = friendId;
                const friend = friends.find(f => f.id === friendId);
                
                document.getElementById('currentFriendName').textContent = friend.name;
                document.getElementById('currentStatus').textContent = 'онлайн';
                const avatar = document.getElementById('currentAvatarSmall');
                avatar.textContent = friend.name[0];
                avatar.style.background = friend.avatar_color;
                
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                document.getElementById('messageInput').focus();
                
                chatHistory = [];
                renderMessages();
                
                if (window.innerWidth <= 768) {
                    document.getElementById('chatsSidebar').classList.add('hide');
                }
            }
            
            function renderMessages() {
                const container = document.getElementById('messagesArea');
                if (chatHistory.length === 0) {
                    container.innerHTML = '<div class="empty-chat"><span>💬</span><p>Напишите что-нибудь другу</p></div>';
                    return;
                }
                
                container.innerHTML = chatHistory.map((msg, idx) => {
                    if (msg.role === 'user') {
                        return `
                            <div class="message-wrapper user">
                                <div class="message-bubble">
                                    ${escapeHtml(msg.content)}
                                    <span class="message-time">${getTime()}</span>
                                    <span class="message-status">✓✓</span>
                                </div>
                            </div>
                        `;
                    } else {
                        const friend = friends.find(f => f.id === msg.friend_id);
                        return `
                            <div class="message-wrapper friend">
                                <div class="message-bubble">
                                    ${escapeHtml(msg.content)}
                                    <span class="message-time">${getTime()}</span>
                                </div>
                            </div>
                        `;
                    }
                }).join('');
                container.scrollTop = container.scrollHeight;
            }
            
            function getTime() {
                const now = new Date();
                return now.getHours().toString().padStart(2, '0') + ':' + 
                       now.getMinutes().toString().padStart(2, '0');
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message || !currentFriendId || isWaiting) return;
                
                chatHistory.push({
                    role: 'user',
                    content: message
                });
                renderMessages();
                
                input.value = '';
                isWaiting = true;
                document.getElementById('sendButton').disabled = true;
                document.getElementById('typingIndicator').style.display = 'flex';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            friend_id: currentFriendId,
                            history: chatHistory.filter(m => m.role === 'user').slice(-10).map(m => ({
                                role: 'user',
                                content: m.content
                            }))
                        })
                    });
                    
                    const data = await response.json();
                    
                    chatHistory.push({
                        role: 'friend',
                        friend_id: data.friend_id,
                        content: data.response
                    });
                    renderMessages();
                    
                } catch (error) {
                    console.error('Error:', error);
                    chatHistory.push({
                        role: 'friend',
                        friend_id: currentFriendId,
                        content: '😅 Ошибка подключения... Попробуй еще раз!'
                    });
                    renderMessages();
                } finally {
                    isWaiting = false;
                    document.getElementById('sendButton').disabled = false;
                    document.getElementById('typingIndicator').style.display = 'none';
                    document.getElementById('messageInput').focus();
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            document.getElementById('sendButton').onclick = sendMessage;
            document.getElementById('messageInput').onkeypress = (e) => {
                if (e.key === 'Enter') sendMessage();
            };
            document.getElementById('backButton').onclick = () => {
                document.getElementById('chatsSidebar').classList.remove('hide');
            };
            
            loadFriends();
        </script>
    </body>
    </html>
    ''')