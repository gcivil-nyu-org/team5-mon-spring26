<script>
    import { onMount } from "svelte";
    import LeftNav from "../components/LeftNav.svelte";
    import BackgroundRings from "../components/BackgroundRings.svelte";
    import TreeChat from "../components/TreeChat.svelte";
    export let navigate;

    let activeTreeId = null;
    let chatStatus = 'connecting';
    let followedChats = [];
    let loadingChats = true;

    onMount(() => {
        const urlParams = new URLSearchParams(window.location.search);
        activeTreeId = urlParams.get('tree');
        fetchChats();
    });

    async function fetchChats() {
        try {
            const res = await fetch('/api/my-followed-trees/', { credentials: 'include' });
            const data = await res.json();
            if (data.success) {
                // Show chats that have messages, OR match the currently active tree
                followedChats = data.trees.filter(t => t.has_messages || String(t.tree_id) === String(activeTreeId));
            }
        } catch (e) {
            console.error("Error fetching chats", e);
        } finally {
            loadingChats = false;
        }
    }

    function selectTree(id) {
        activeTreeId = id;
        chatStatus = 'connecting';
        window.history.pushState({}, "", `/chat?tree=${id}`);
        
        // If the chat isn't already the active one in the list UI, we don't strictly need to refetch yet,
        // but ensuring it remains visible if it was just initiated is handled by the socket sending messages.
    }

    function handleStatusChange(e) {
        chatStatus = e.detail.status;
    }
</script>

<div class="page">
    <BackgroundRings />
    <LeftNav {navigate} activePage="chat" />

    <div class="chat-layout">
        <div class="chat-list">
            <div class="chat-list-header">
                <h2>Messages</h2>
                <input
                    class="chat-search"
                    type="text"
                    placeholder="Search chats..."
                />
            </div>

            <div class="chat-list-scroll" style="overflow-y: auto; flex: 1; padding-bottom: 1rem;">
                {#if loadingChats}
                    <div style="padding: 2.5rem 1.5rem; text-align: center; color: var(--sage); font-size: 0.9rem;">
                        Loading your chats...
                    </div>
                {:else if followedChats.length > 0}
                    <div class="section-label" style="padding: 1rem 1.5rem 0.5rem; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--sage); font-weight: 600;">Active Group Chats</div>
                    {#each followedChats as chat}
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                        <div class="chat-item" class:active={String(activeTreeId) === String(chat.tree_id)} on:click={() => selectTree(chat.tree_id)}>
                            <div class="chat-item-icon">🌳</div>
                            <div class="chat-item-info">
                                <strong>{chat.tree_name} Chat</strong>
                                <small class="sidebar-status {String(activeTreeId) === String(chat.tree_id) ? chatStatus : ''}">
                                    {#if String(activeTreeId) === String(chat.tree_id)}
                                        {#if chatStatus === 'connected'}
                                            ● Connected — Real-time
                                        {:else if chatStatus === 'connecting'}
                                            ◌ Connecting...
                                        {:else if chatStatus === 'disconnected'}
                                            ○ Disconnected
                                        {:else}
                                            ✕ Connection Error
                                        {/if}
                                    {:else}
                                        <span style="color: var(--sage); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; display: inline-block;">
                                            {chat.last_message || 'Start chatting...'}
                                        </span>
                                    {/if}
                                </small>
                            </div>
                            <div class="chat-item-right">
                                <span class="chat-item-time">
                                    {chat.last_message_time ? new Date(chat.last_message_time).toLocaleDateString([], {month: 'short', day: 'numeric'}) : 'Now'}
                                </span>
                            </div>
                        </div>
                    {/each}
                {:else}
                    <div style="padding: 2.5rem 1.5rem; text-align: center; color: var(--sage); display: flex; flex-direction: column; align-items: center; gap: 0.5rem; margin-top: 1rem;">
                        <div style="font-size: 2.5rem; opacity: 0.4;">💬</div>
                        <h4 style="font-family: 'DM Sans', sans-serif; font-weight: 500; font-size: 0.95rem; color: #2c1810; margin: 0;">No Active Chats</h4>
                        <p style="font-size: 0.8rem; line-height: 1.4; opacity: 0.8; margin: 0;">Visit any tree's dashboard and tap "Group Chat" to join the conversation!</p>
                    </div>
                {/if}
            </div>
        </div>

        <div class="chat-main" style="background: transparent;">
            {#if activeTreeId}
                <TreeChat treeId={activeTreeId} on:statusChange={handleStatusChange} />
            {:else}
                <div class="empty-chat" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--sage);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🌳</div>
                    <h3 style="font-family: 'Playfair Display', serif; color: var(--bark);">Select a Chat</h3>
                    <p>Choose a leaf from the community tree to start talking.</p>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    :root {
        --bark: #282119;
        --moss: #2A4027;
        --sage: #758F6F;
        --leaf: #A7C5A3;
        --canopy: #E5EDE3;
        --cream: #FAF8F5;
        --mist: #F2F5F0;
        --sun: #DCAE5A;
        --ink: #111511;
        --shadow: rgba(40, 33, 25, 0.08);
        --glass-bg: rgba(250, 248, 245, 0.85);
        --glass-border: rgba(255, 255, 255, 0.4);
    }

    .page {
        background: url('/noise.png'), linear-gradient(145deg, var(--mist) 0%, #E8EFDF 100%);
        box-shadow: inset 0 0 100px rgba(0,0,0,0.02);
        min-height: 100vh;
        padding-left: 60px;
        color: var(--ink);
        position: relative;
        z-index: 0;
        overflow: hidden;
    }
    .chat-layout {
        height: calc(100vh - 60px);
        display: grid;
        grid-template-columns: 320px 1fr;
        padding: 1.5rem 1.5rem 1.5rem 0;
        gap: 1.5rem;
        max-width: 1600px;
        margin: 0 auto;
    }
    .chat-list {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(42, 64, 39, 0.06), 0 2px 10px rgba(0,0,0,0.02);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .sidebar-status {
        transition: color 0.3s ease;
        font-weight: 500;
    }
    .sidebar-status.connected { color: #3A8B49 !important; }
    .sidebar-status.connecting { color: #CCA13A !important; }
    .sidebar-status.disconnected { color: #D64545 !important; }
    .sidebar-status.error { color: #D64545 !important; }

    .chat-list-header {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        background: linear-gradient(to bottom, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0) 100%);
    }
    .chat-list-header h2 {
        font-family: "Outfit", "DM Sans", sans-serif;
        font-weight: 700;
        font-size: 1.6rem;
        color: var(--moss);
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    .chat-search {
        width: 100%;
        padding: 0.7rem 1rem;
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(117,143,111,0.2);
        border-radius: 12px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        outline: none;
        color: var(--ink);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
    }
    .chat-search:focus {
        background: #fff;
        border-color: var(--sage);
        box-shadow: 0 0 0 3px rgba(117,143,111,0.15);
    }
    .section-label {
        padding: 1rem 1.5rem 0.5rem;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--sage);
    }
    .chat-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border-bottom: 1px solid rgba(0,0,0,0.03);
        position: relative;
    }
    .chat-item:hover {
        background: rgba(255,255,255,0.5);
    }
    .chat-item.active {
        background: linear-gradient(135deg, var(--mist), #fff);
        box-shadow: inset 3px 0 0 var(--moss);
    }
    .chat-item.active::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(to right, rgba(42, 64, 39, 0.05) 0%, transparent 100%);
        pointer-events: none;
    }
    .chat-item.active strong {
        color: var(--moss);
        font-weight: 700;
    }
    .chat-item-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, #4F774A, var(--moss));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(42, 64, 39, 0.2);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    .chat-item-info {
        flex: 1;
        min-width: 0;
        z-index: 1;
    }
    .chat-item-info strong {
        display: block;
        font-family: "Outfit", sans-serif;
        font-size: 0.95rem;
        color: var(--ink);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.1rem;
    }
    .chat-item-info small {
        font-family: "DM Sans", sans-serif;
        font-size: 0.8rem;
        color: var(--sage);
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .chat-item-time {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--sage);
        letter-spacing: 0.05em;
    }
    .chat-item-right {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.4rem;
        z-index: 1;
    }
    .unread-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--sun);
        box-shadow: 0 0 8px rgba(220, 174, 90, 0.5);
        flex-shrink: 0;
    }

    .chat-main {
        display: flex;
        flex-direction: column;
        height: 100%;
        border-radius: 24px;
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        box-shadow: 0 10px 40px rgba(42, 64, 39, 0.06);
        overflow: hidden;
    }
    .chat-header-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    .chat-header-info {
        flex: 1;
    }
    .chat-header-info strong {
        display: block;
        font-size: 1rem;
        color: #a44a3f; /* Redwood Rust header */
    }
    .chat-header-info small {
        font-size: 0.78rem;
        color: var(--sage);
    }
    .chat-header-actions {
        display: flex;
        gap: 0.5rem;
    }
    .chat-header-btn {
        background: var(--mist);
        border: none;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        cursor: pointer;
        color: var(--sage);
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        transition: background 0.2s;
        font-family: "DM Sans", sans-serif;
    }
    .chat-header-btn:hover {
        background: var(--canopy);
        color: var(--moss);
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        background: var(--mist);
    }
    .msg-system {
        text-align: center;
        background: rgba(61, 90, 62, 0.1);
        border: 1px solid rgba(61, 90, 62, 0.2);
        color: var(--moss);
        font-size: 0.78rem;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.5rem auto;
        max-width: 400px;
        font-weight: 500;
    }
    .msg-announcement {
        background: rgba(212, 168, 83, 0.1);
        border: 1px solid rgba(212, 168, 83, 0.3);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
    }
    .ann-icon {
        font-size: 1rem;
        flex-shrink: 0;
    }
    .ann-text strong {
        display: block;
        font-size: 0.8rem;
        color: #8b4513;
        margin-bottom: 0.2rem;
    }
    .ann-text p {
        font-size: 0.85rem;
        color: var(--ink);
        margin: 0;
    }
    .ann-text small {
        font-size: 0.72rem;
        color: var(--sage);
    }
    .msg-group {
        display: flex;
        gap: 0.8rem;
        align-items: flex-end;
    }
    .msg-group.mine {
        flex-direction: row-reverse;
    }
    .msg-sender-ava {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--sage), var(--canopy));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    .msg-sender-ava.caretaker {
        background: linear-gradient(135deg, var(--bark), #8b4513);
    }
    .msg-bubble {
        max-width: 65%;
        background: #faf9f6; /* Warm White received msg */
        border: 1px solid #36454f;
        border-radius: 18px 18px 18px 4px;
        padding: 0.7rem 1rem;
        box-shadow: 0 1px 6px rgba(138, 154, 91, 0.05);
        color: #2b2b2b;
    }
    .msg-group.mine .msg-bubble {
        background: #36454f; /* Charcoal Gray sent msg */
        color: #faf9f6; /* Contrasting text */
        border-radius: 18px 18px 4px 18px;
        border: none;
    }
    .msg-sender-name {
        font-size: 0.72rem;
        font-weight: 600;
        color: #a44a3f; /* Redwood Rust sender */
        margin-bottom: 0.2rem;
    }
    .msg-group.mine .msg-sender-name {
        color: rgba(255, 255, 255, 0.7);
    }
    .msg-text {
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .msg-group.mine .msg-text {
        color: white;
    }
    .msg-time {
        font-size: 0.68rem;
        color: var(--canopy);
        margin-top: 0.2rem;
        text-align: right;
    }
    .msg-group.mine .msg-time {
        color: rgba(255, 255, 255, 0.6);
    }

    .chat-input-bar {
        background: white;
        border-top: 1px solid var(--canopy);
        padding: 1rem 1.5rem;
        display: flex;
        align-items: flex-end;
        gap: 0.8rem;
    }
    .chat-input-wrap {
        flex: 1;
        background: var(--mist);
        border-radius: 12px;
        padding: 0.7rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .chat-input {
        flex: 1;
        border: none;
        background: none;
        outline: none;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        color: var(--ink);
        resize: none;
        min-height: 24px;
        max-height: 120px;
    }
    .chat-input::placeholder {
        color: var(--canopy);
    }
    .chat-emoji-btn {
        background: none;
        border: none;
        font-size: 1.1rem;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .chat-emoji-btn:hover {
        transform: scale(1.2);
    }
    .chat-send-btn {
        background: var(--moss);
        color: white;
        border: none;
        border-radius: 12px;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 1.1rem;
    }
    .chat-send-btn:hover {
        background: var(--bark);
        transform: scale(1.05);
    }
</style>
