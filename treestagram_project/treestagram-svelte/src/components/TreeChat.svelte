<script>
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    export let treeId;
    
    const dispatch = createEventDispatcher();

    let messages = [];
    let newMessage = '';
    let socket;
    let chatContainer;
    let connectionStatus = 'connecting'; // 'connecting', 'connected', 'disconnected', 'error', 'access_denied'
    let accessDeniedMsg = '';

    // Reactively connect when treeId changes
    $: if (treeId) {
        if (socket) {
            socket.close();
            socket = null;
        }
        messages = [];
        accessDeniedMsg = '';
        connectWebSocket();
    }

    function connectWebSocket() {
        connectionStatus = 'connecting';
        dispatch('statusChange', { status: 'connecting' });

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${treeId}/`);

        socket.onopen = function() {
            connectionStatus = 'connected';
            dispatch('statusChange', { status: 'connected' });
        };

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'access_denied') {
                connectionStatus = 'access_denied';
                accessDeniedMsg = data.message;
                dispatch('statusChange', { status: 'access_denied' });
                return;
            }
            messages = [...messages, data];
            scrollToBottom();
        };

        socket.onclose = function(e) {
            connectionStatus = 'disconnected';
            dispatch('statusChange', { status: 'disconnected' });
            console.error('Chat socket closed unexpectedly');
        };

        socket.onerror = function(e) {
            connectionStatus = 'error';
            dispatch('statusChange', { status: 'error' });
        };
    }

    onDestroy(() => {
        if (socket) {
            socket.close();
        }
    });

    function sendMessage() {
        if (newMessage.trim() === '' || connectionStatus !== 'connected') return;
        socket.send(JSON.stringify({
            'message': newMessage
        }));
        newMessage = '';
    }

    function scrollToBottom() {
        if (chatContainer) {
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 50);
        }
    }

    function formatTime(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
</script>

<div class="chat-wrapper">
    <div class="chat-header">
        <h4>Live Group Chat (Tree #{treeId})</h4>
        <span class="live-indicator {connectionStatus}">
            {#if connectionStatus === 'connected'}
                ● Live
            {:else if connectionStatus === 'connecting'}
                ◌ Connecting...
            {:else if connectionStatus === 'disconnected'}
                ○ Disconnected
            {:else}
                ✕ Error
            {/if}
        </span>
    </div>
    
    {#if connectionStatus === 'access_denied'}
        <div class="access-denied-overlay">
            <div class="access-denied-card">
                <span class="lock-icon">🔒</span>
                <h3>Follow to Join</h3>
                <p>{accessDeniedMsg}</p>
                <p class="hint">Go to this tree's dashboard and click <strong>🌟 Follow Tree</strong> to unlock the group chat.</p>
            </div>
        </div>
    {:else}
    <div class="chat-messages" bind:this={chatContainer}>
        {#if messages.length === 0}
            <div class="no-messages">No messages yet. Start the conversation!</div>
        {/if}
        {#each messages as msg}
            <div class="message {msg.user === 'Anonymous Observer' ? 'system-msg' : ''} {msg.user === 'TreeBot 🤖' ? 'bot-msg' : ''} {msg.user === 'System' ? 'system-banner' : ''}">
                <div class="msg-avatar">
                    {#if msg.user === 'TreeBot 🤖'}
                        🤖
                    {:else if msg.user === 'System'}
                        🌱
                    {:else}
                        {(msg.user || '?')[0].toUpperCase()}
                    {/if}
                </div>
                <div class="msg-content">
                    <div class="msg-meta">
                        <span class="msg-author">@{msg.user}</span>
                        <span class="msg-time">{formatTime(msg.timestamp)}</span>
                    </div>
                    <div class="msg-text">{msg.message}</div>
                </div>
            </div>
        {/each}
    </div>
    
    <div class="chat-input-area">
        <input 
            type="text" 
            bind:value={newMessage} 
            on:keypress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..." 
        />
        <button on:click={sendMessage} disabled={!newMessage.trim()}>Send</button>
    </div>
    {/if}
</div>

<style>
    .chat-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: transparent;
    }
    
    .chat-header {
        padding: 1.5rem 2rem;
        background: linear-gradient(to right, rgba(255,255,255,0.7), rgba(255,255,255,0.1));
        border-bottom: 1px solid rgba(0,0,0,0.05);
        color: #282119;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(10px);
    }
    .chat-header h4 {
        margin: 0;
        font-family: "Outfit", sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #2A4027; /* moss */
    }
    .live-indicator {
        font-size: 0.75rem;
        font-weight: 700;
        font-family: "Outfit", sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: color 0.3s;
    }
    .live-indicator.connected {
        color: #3A8B49;
        animation: pulse 2s infinite;
    }
    .live-indicator.connecting {
        color: #CCA13A;
        animation: pulse 1s infinite;
    }
    .live-indicator.disconnected { color: #D64545; animation: none; }
    .live-indicator.error { color: #D64545; animation: none; }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .chat-messages {
        flex: 1;
        padding: 1.5rem 2rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        background: transparent;
    }
    .no-messages {
        text-align: center;
        color: #758F6F; /* sage */
        font-family: "DM Sans", sans-serif;
        font-size: 1rem;
        margin-top: 3rem;
        background: rgba(255,255,255,0.4);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(5px);
    }
    
    .message {
        display: flex;
        gap: 1rem;
        align-items: flex-end;
    }
    .msg-avatar {
        width: 40px;
        height: 40px;
        border-radius: 14px;
        background: linear-gradient(135deg, #A7C5A3, #2A4027);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-family: "Outfit", sans-serif;
        font-size: 1.1rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(42, 64, 39, 0.15);
        border: 1px solid rgba(255,255,255,0.3);
    }
    .msg-content {
        max-width: 75%;
        display: flex;
        flex-direction: column;
    }
    .msg-meta {
        display: flex;
        align-items: baseline;
        gap: 0.6rem;
        margin-bottom: 0.3rem;
        padding-left: 0.2rem;
    }
    .msg-author {
        font-family: "Outfit", sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        color: #282119;
    }
    .msg-time {
        font-family: "DM Sans", sans-serif;
        font-size: 0.7rem;
        color: rgba(40, 33, 25, 0.5);
    }
    .msg-text {
        font-family: "DM Sans", sans-serif;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #111511;
        background: #fff;
        padding: 0.9rem 1.2rem;
        border-radius: 16px 16px 16px 4px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03), 0 1px 3px rgba(0,0,0,0.02);
        border: 1px solid rgba(0,0,0,0.02);
        word-wrap: break-word;
    }
    
    /* Bot Message Styling Overrides */
    .message.bot-msg .msg-avatar {
        background: linear-gradient(135deg, #1e4d30, #0a2613); 
        color: #a8ffb2;
        font-size: 1.4rem;
    }
    .message.bot-msg .msg-text {
        background: linear-gradient(135deg, #f0f7f1, #e3f0e5);
        border: 1px solid rgba(42, 64, 39, 0.1);
        color: #1a3622;
        border-radius: 16px 16px 16px 4px;
    }
    .message.bot-msg .msg-author {
        color: #1e4d30;
    }

    /* Input Area - Floating sleek pill */
    .chat-input-area {
        display: flex;
        padding: 1rem 2rem 1.5rem;
        background: transparent;
        gap: 1rem;
    }
    .chat-input-area input {
        flex: 1;
        padding: 1rem 1.5rem;
        border-radius: 24px;
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(0,0,0,0.06);
        font-family: "DM Sans", sans-serif;
        font-size: 1rem;
        outline: none;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        backdrop-filter: blur(10px);
    }
    .chat-input-area input:focus {
        background: #fff;
        border-color: #758F6F;
        box-shadow: 0 8px 30px rgba(117,143,111,0.1);
        transform: translateY(-1px);
    }
    .chat-input-area button {
        background: linear-gradient(135deg, #758F6F, #2A4027);
        color: white;
        border: none;
        padding: 0 2rem;
        border-radius: 24px;
        font-family: "Outfit", sans-serif;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(42, 64, 39, 0.25);
    }
    .chat-input-area button:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(42, 64, 39, 0.3);
    }
    .chat-input-area button:disabled {
        background: #d1d9cf;
        color: #9ab09a;
        box-shadow: none;
        cursor: not-allowed;
    }

    /* Access Denied Overlay */
    .access-denied-overlay {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    .access-denied-card {
        text-align: center;
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 360px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 8px 30px rgba(0,0,0,0.05);
    }
    .lock-icon {
        font-size: 2.5rem;
        display: block;
        margin-bottom: 0.8rem;
    }
    .access-denied-card h3 {
        font-family: "Outfit", sans-serif;
        font-size: 1.3rem;
        color: #2A4027;
        margin: 0 0 0.6rem;
    }
    .access-denied-card p {
        font-family: "DM Sans", sans-serif;
        color: #555;
        font-size: 0.95rem;
        margin: 0 0 0.5rem;
        line-height: 1.5;
    }
    .access-denied-card .hint {
        font-size: 0.82rem;
        color: #888;
    }

    /* System Banner Styling */
    .message.system-banner .msg-avatar {
        background: linear-gradient(135deg, #34a855, #1b6b30);
        font-size: 1.2rem;
    }
    .message.system-banner .msg-text {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border: 1px solid rgba(76, 175, 80, 0.15);
        color: #1b5e20;
        font-weight: 600;
        font-style: italic;
    }
    .message.system-banner .msg-author {
        color: #2e7d32;
    }
</style>
