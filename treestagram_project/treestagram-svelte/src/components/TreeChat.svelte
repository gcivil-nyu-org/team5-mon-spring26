<script>
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    export let treeId;
    export let treeName = '';
    
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
        // socket = new WebSocket(`${protocol}//localhost:8000/ws/chat/${treeId}/`);
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
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <h4 
            on:click={() => window.navigate(`/treedashboard/${treeId}`)}
            title="Go to Tree Dashboard"
        >
            {treeName} <span style="color: #60af77; font-weight: 500; font-size: 0.9em; margin-left: 0.3em;">(#{treeId})</span>
        </h4>
        <span class="live-indicator {connectionStatus}">
            {#if connectionStatus === 'connected'}
                Live
            {:else if connectionStatus === 'connecting'}
                Connecting...
            {:else if connectionStatus === 'disconnected'}
                Disconnected
            {:else}
                Error
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
        background: url('/noise.png'), var(--mist);
        border-radius: 0 24px 24px 0;
        overflow: hidden;
        position: relative;
    }
    /* Subtle botanical background overlay extending behind everything */
    .chat-wrapper::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url('/chat_bg.png');
        background-repeat: repeat;
        background-size: 400px;
        opacity: 0.9;
        mix-blend-mode: multiply;
        pointer-events: none;
        z-index: 0;
    }
    
    /* ─── Header ────────────────────────────────────────────────────── */
    .chat-header {
        padding: 1.2rem 2rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,247,241,0.95));
        border-bottom: 1px solid rgba(42, 64, 39, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        z-index: 10;
        position: relative;
    }
    .chat-header h4 {
        margin: 0;
        font-family: "Outfit", sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a2e18;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: color 0.2s ease, transform 0.2s ease;
    }
    .chat-header h4:hover {
        color: #3A8B49;
    }
    .chat-header h4:active {
        transform: scale(0.98);
    }
    .chat-header h4::before {
        content: '🌿';
        font-size: 1.1rem;
    }
    .live-indicator {
        font-size: 0.75rem;
        font-weight: 700;
        font-family: "Outfit", sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        background: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        gap: 0.4rem;
        transition: all 0.3s;
    }
    .live-indicator::before {
        content: '';
        display: block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .live-indicator.connected { color: #3A8B49; border: 1px solid rgba(58, 139, 73, 0.2); }
    .live-indicator.connected::before { background: #3A8B49; animation: pulse-green 2s infinite; }
    .live-indicator.connecting { color: #CCA13A; border: 1px solid rgba(204, 161, 58, 0.2); }
    .live-indicator.connecting::before { background: #CCA13A; animation: pulse-yellow 1s infinite; }
    .live-indicator.disconnected, .live-indicator.error { color: #D64545; border: 1px solid rgba(214, 69, 69, 0.2); }
    .live-indicator.disconnected::before, .live-indicator.error::before { background: #D64545; }

    @keyframes pulse-green { 0%, 100% { box-shadow: 0 0 0 0 rgba(58, 139, 73, 0.4); } 50% { box-shadow: 0 0 0 4px rgba(58, 139, 73, 0); } }
    @keyframes pulse-yellow { 0%, 100% { box-shadow: 0 0 0 0 rgba(204, 161, 58, 0.4); } 50% { box-shadow: 0 0 0 4px rgba(204, 161, 58, 0); } }
    
    /* ─── Messages Area ─────────────────────────────────────────────── */
    .chat-messages {
        flex: 1;
        padding: 2rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        position: relative;
        z-index: 1; /* Place above the wrapper's botanical background */
    }
    
    .no-messages {
        text-align: center;
        color: #5c7556;
        font-family: "DM Sans", sans-serif;
        font-size: 0.95rem;
        margin-top: auto;
        margin-bottom: auto;
        background: rgba(255,255,255,0.7);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 4px 20px rgba(42, 64, 39, 0.05);
        align-self: center;
        z-index: 1;
    }
    
    .message {
        display: flex;
        gap: 0.8rem;
        align-items: flex-end;
        z-index: 1;
        animation: fadeInMsg 0.3s ease-out forwards;
    }
    @keyframes fadeInMsg {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .msg-avatar {
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: linear-gradient(135deg, #A7C5A3, #4F774A);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-family: "Outfit", sans-serif;
        font-size: 1rem;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(42, 64, 39, 0.15);
        border: 2px solid white;
    }
    
    .msg-content {
        max-width: 70%;
        display: flex;
        flex-direction: column;
    }
    .msg-meta {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        margin-bottom: 0.3rem;
        padding-left: 0.4rem;
    }
    .msg-author {
        font-family: "Outfit", sans-serif;
        font-weight: 700;
        font-size: 0.8rem;
        color: #3b2f24;
    }
    .msg-time {
        font-family: "DM Sans", sans-serif;
        font-size: 0.65rem;
        color: #8c857d;
        font-weight: 500;
    }
    .msg-text {
        font-family: "DM Sans", sans-serif;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #1a1a1a;
        background: white;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
        border: 1px solid rgba(0,0,0,0.03);
        word-wrap: break-word;
        position: relative;
    }
    
    /* Sent Message Bubble styling (we apply this to 'mine' but currently all are rendered same, so we'll just style all nicely) */
    
    /* Bot Message Styling Overrides */
    .message.bot-msg .msg-avatar {
        background: linear-gradient(135deg, #2A4027, #132411); 
        color: #e5ffea;
        font-size: 1.2rem;
    }
    .message.bot-msg .msg-text {
        background: linear-gradient(to right, #f4fbf4, #ebf5ec);
        border: 1px solid rgba(42, 64, 39, 0.1);
        color: #1a3622;
        border-radius: 4px 18px 18px 18px;
    }
    .message.bot-msg .msg-author {
        color: #1e4d30;
    }

    /* System Banner Styling */
    .message.system-banner {
        align-self: center;
        margin: 1rem 0;
    }
    .message.system-banner .msg-avatar {
        display: none;
    }
    .message.system-banner .msg-meta {
        display: none;
    }
    .message.system-banner .msg-text {
        background: rgba(117, 143, 111, 0.1);
        border: 1px solid rgba(117, 143, 111, 0.2);
        color: #3b5236;
        font-weight: 600;
        font-size: 0.8rem;
        border-radius: 20px;
        padding: 0.4rem 1.2rem;
        box-shadow: none;
        text-align: center;
    }

    /* ─── Input Area ────────────────────────────────────────────────── */
    .chat-input-area {
        display: flex;
        padding: 1.5rem 2rem;
        background: transparent;
        gap: 1rem;
        z-index: 10;
        position: relative;
    }
    .chat-input-area input {
        flex: 1;
        padding: 1rem 1.5rem;
        border-radius: 24px;
        background: rgba(255,255,255,0.6);
        border: 1px solid rgba(255,255,255,0.9);
        font-family: "DM Sans", sans-serif;
        font-size: 0.95rem;
        color: #1a2e18;
        outline: none;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: inset 0 2px 8px rgba(42, 64, 39, 0.05), 0 4px 15px rgba(0,0,0,0.03);
    }
    .chat-input-area input::placeholder {
        color: #8c9c8a;
        font-weight: 500;
    }
    .chat-input-area input:focus {
        background: rgba(255,255,255,0.9);
        border-color: #A7C5A3;
        box-shadow: 0 6px 20px rgba(82, 154, 103, 0.12), inset 0 2px 4px rgba(0,0,0,0.02);
        transform: translateY(-1px);
    }
    .chat-input-area button {
        background: linear-gradient(135deg, #529A67, #2A4027);
        color: white;
        border: none;
        padding: 0 1.8rem;
        border-radius: 24px;
        font-family: "Outfit", sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(42, 64, 39, 0.25);
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .chat-input-area button::after {
        content: '↗';
        font-size: 1.1rem;
        transition: transform 0.3s;
    }
    .chat-input-area button:hover:not(:disabled) {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(42, 64, 39, 0.35);
        background: linear-gradient(135deg, #60af77, #355031);
    }
    .chat-input-area button:hover:not(:disabled)::after {
        transform: translate(2px, -2px);
    }
    .chat-input-area button:disabled {
        background: linear-gradient(135deg, rgba(82, 154, 103, 0.3), rgba(42, 64, 39, 0.2));
        color: rgba(255,255,255,0.9);
        box-shadow: none;
        cursor: not-allowed;
    }
    .chat-input-area button:disabled::after {
        opacity: 0.5;
    }

    /* ─── Access Denied Overlay ─────────────────────────────────────── */
    .access-denied-overlay {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: rgba(255,255,255,0.4);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .access-denied-card {
        text-align: center;
        background: white;
        border-radius: 24px;
        padding: 3rem 2.5rem;
        max-width: 400px;
        border: 1px solid rgba(42, 64, 39, 0.1);
        box-shadow: 0 12px 40px rgba(42, 64, 39, 0.08), 0 4px 12px rgba(0,0,0,0.03);
        animation: scaleUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes scaleUp {
        from { opacity: 0; transform: scale(0.95) translateY(10px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
    .lock-icon {
        font-size: 3rem;
        display: inline-block;
        margin-bottom: 1rem;
        background: #f4fbf4;
        width: 80px;
        height: 80px;
        line-height: 80px;
        border-radius: 50%;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.04);
        border: 1px solid rgba(82, 154, 103, 0.2);
    }
    .access-denied-card h3 {
        font-family: "Outfit", sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a2e18;
        margin: 0 0 0.8rem;
    }
    .access-denied-card p {
        font-family: "DM Sans", sans-serif;
        color: #5c7556;
        font-size: 1rem;
        margin: 0 0 1.5rem;
        line-height: 1.6;
    }
    .access-denied-card .hint {
        font-size: 0.85rem;
        color: #8c857d;
        background: #faf8f5;
        padding: 1rem;
        border-radius: 12px;
        border: 1px dashed rgba(140, 133, 125, 0.3);
    }
</style>
