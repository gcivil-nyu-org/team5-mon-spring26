<script>
    import TopNav from "../components/TopNav.svelte";
    export let navigate;
</script>

<div class="page">
    <TopNav {navigate} activePage="chat" />

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
            <div class="section-label">Group Chats</div>
            <div class="chat-item active">
                <div class="chat-item-icon">🌳</div>
                <div class="chat-item-info">
                    <strong>Elm #00482 Fan Chat</strong>
                    <small
                        >brooklyn_botanist: ⚠️ Caretaker Update: Noticed...</small
                    >
                </div>
                <div class="chat-item-right">
                    <span class="chat-item-time">2h</span>
                    <div class="unread-dot"></div>
                </div>
            </div>
            <div class="chat-item">
                <div class="chat-item-icon">🌿</div>
                <div class="chat-item-info">
                    <strong>Ginkgo #10293 Fans</strong>
                    <small>treelover: Someone left trash bags again...</small>
                </div>
                <span class="chat-item-time">5h</span>
            </div>
            <div class="chat-item">
                <div class="chat-item-icon">🍁</div>
                <div class="chat-item-info">
                    <strong>Maple #03312 Chat</strong>
                    <small>You: The colors this fall were incredible!</small>
                </div>
                <span class="chat-item-time">1d</span>
            </div>
            <div class="chat-item">
                <div class="chat-item-icon">🌲</div>
                <div class="chat-item-info">
                    <strong>Oak #55721 Community</strong>
                    <small>admin: New caretaker applications open</small>
                </div>
                <span class="chat-item-time">2d</span>
            </div>
            <div class="section-label border-top">Direct Messages</div>
            <div class="chat-item">
                <div class="chat-item-icon dm">🧑</div>
                <div class="chat-item-info">
                    <strong>treewhisperer_nyc</strong>
                    <small>Did you see the new growth on that elm?</small>
                </div>
                <span class="chat-item-time">3h</span>
            </div>
            <div class="chat-item">
                <div class="chat-item-icon dm">👩</div>
                <div class="chat-item-info">
                    <strong>brooklyn_botanist</strong>
                    <small>Thanks for the heads up on the roots!</small>
                </div>
                <span class="chat-item-time">1d</span>
            </div>
        </div>

        <div class="chat-main">
            <div class="chat-header">
                <div class="chat-header-icon">🌳</div>
                <div class="chat-header-info">
                    <strong>Elm #00482 Fan Chat</strong>
                    <small
                        >127 fans · American Elm, Central Park W & 72nd ·
                        Health: Good</small
                    >
                </div>
                <div class="chat-header-actions">
                    <button
                        class="chat-header-btn"
                        on:click={() => navigate("/dashboard")}
                        >🌳 View Tree</button
                    >
                    <button class="chat-header-btn">👥 Members</button>
                </div>
            </div>

            <div class="chat-messages">
                <div class="msg-system">📅 Today, February 27, 2026</div>

                <div class="msg-announcement">
                    <span class="ann-icon">📢</span>
                    <div class="ann-text">
                        <strong
                            >🛡️ Caretaker Announcement from brooklyn_botanist</strong
                        >
                        <p>
                            Health inspection completed. Tree is doing well but
                            we need to watch the sidewalk crack near the base —
                            filed a formal report with Parks Dept. Expires in
                            24h.
                        </p>
                        <small>2 hours ago</small>
                    </div>
                </div>

                <div class="msg-group">
                    <div class="msg-sender-ava">🧑</div>
                    <div>
                        <div class="msg-bubble">
                            <div class="msg-sender-name">
                                treewhisperer_nyc · Credible
                            </div>
                            <div class="msg-text">
                                Just walked by this morning — the new growth
                                since last week is incredible! Anyone else
                                noticing how fast it's bouncing back from the
                                summer heat? 🌱
                            </div>
                            <div class="msg-time">10:32 AM</div>
                        </div>
                    </div>
                </div>

                <div class="msg-group">
                    <div class="msg-sender-ava">👩</div>
                    <div>
                        <div class="msg-bubble">
                            <div class="msg-sender-name">central_park_fan</div>
                            <div class="msg-text">
                                Yes! I posted a photo yesterday. The bark is
                                looking really clean too, no fungal patches.
                                This tree is in great hands 🙌
                            </div>
                            <div class="msg-time">10:45 AM</div>
                        </div>
                    </div>
                </div>

                <div class="msg-group mine">
                    <div class="msg-sender-ava">🌿</div>
                    <div>
                        <div class="msg-bubble">
                            <div class="msg-sender-name">You</div>
                            <div class="msg-text">
                                I measured the canopy spread last weekend — it's
                                expanded by about 3 feet this season! Someone
                                put a new bench nearby too which is nice. The
                                roots might push through sidewalk though.
                            </div>
                            <div class="msg-time">11:02 AM</div>
                        </div>
                    </div>
                </div>

                <div class="msg-group">
                    <div class="msg-sender-ava caretaker">🧑</div>
                    <div>
                        <div class="msg-bubble">
                            <div class="msg-sender-name">
                                brooklyn_botanist · 🛡️ Caretaker
                            </div>
                            <div class="msg-text">
                                That root growth is exactly what I reported! The
                                Parks Dept has it on their radar now. In the
                                meantime, please ask visitors not to lean bikes
                                against the trunk 🙏
                            </div>
                            <div class="msg-time">11:18 AM</div>
                        </div>
                    </div>
                </div>

                <div class="msg-system">
                    🌧️ NYC rain forecast: 0.8 inches this weekend — good news
                    for hydration!
                </div>
            </div>

            <div class="chat-input-bar">
                <div class="chat-input-wrap">
                    <button class="chat-emoji-btn">📎</button>
                    <textarea
                        class="chat-input"
                        rows="1"
                        placeholder="Message Elm #00482 community..."
                    ></textarea>
                    <button class="chat-emoji-btn">😊</button>
                </div>
                <button class="chat-send-btn">➤</button>
            </div>
        </div>
    </div>
</div>

<style>
    :root {
        --bark: #2c1810;
        --moss: #3d5a3e;
        --sage: #6b8f71;
        --leaf: #8fbc8f;
        --canopy: #c5d5c5;
        --cream: #f5f0e8;
        --mist: #e8ede8;
        --sun: #d4a853;
        --ink: #1a1108;
        --shadow: rgba(44, 24, 16, 0.12);
    }

    .page {
        background: var(--mist);
        min-height: 100vh;
    }

    .chat-layout {
        height: calc(100vh - 60px);
        display: grid;
        grid-template-columns: 300px 1fr;
    }
    .chat-list {
        background: white;
        border-right: 1px solid var(--canopy);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .chat-list-header {
        padding: 1.2rem;
        border-bottom: 1px solid var(--mist);
    }
    .chat-list-header h2 {
        font-family: "Playfair Display", serif;
        font-size: 1.3rem;
        color: var(--bark);
        margin-bottom: 0.8rem;
    }
    .chat-search {
        width: 100%;
        padding: 0.5rem 0.8rem;
        background: var(--mist);
        border: none;
        border-radius: 8px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        outline: none;
        color: var(--ink);
    }
    .section-label {
        padding: 0.6rem 1.2rem;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
    }
    .section-label.border-top {
        border-top: 1px solid var(--mist);
    }
    .chat-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem 1.2rem;
        cursor: pointer;
        transition: background 0.15s;
        border-bottom: 1px solid var(--mist);
    }
    .chat-item:hover {
        background: var(--mist);
    }
    .chat-item.active {
        background: rgba(61, 90, 62, 0.08);
        border-left: 3px solid var(--moss);
    }
    .chat-item-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .chat-item-icon.dm {
        background: linear-gradient(135deg, var(--bark), #8b4513);
        border-radius: 50%;
    }
    .chat-item-info {
        flex: 1;
        min-width: 0;
    }
    .chat-item-info strong {
        display: block;
        font-size: 0.88rem;
        color: var(--ink);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .chat-item-info small {
        font-size: 0.75rem;
        color: var(--sage);
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .chat-item-time {
        font-size: 0.7rem;
        color: var(--canopy);
    }
    .chat-item-right {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.3rem;
    }
    .unread-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--moss);
        flex-shrink: 0;
    }

    .chat-main {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .chat-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        background: white;
        border-bottom: 1px solid var(--canopy);
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
        color: var(--ink);
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
        background: white;
        border-radius: 18px 18px 18px 4px;
        padding: 0.7rem 1rem;
        box-shadow: 0 1px 6px var(--shadow);
    }
    .msg-group.mine .msg-bubble {
        background: var(--moss);
        color: white;
        border-radius: 18px 18px 4px 18px;
    }
    .msg-sender-name {
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--sage);
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
