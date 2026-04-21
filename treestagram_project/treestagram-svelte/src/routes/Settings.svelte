<script>
    import LeftNav from "../components/LeftNav.svelte";
    import { theme } from "../theme.js";
    import {
        user,
        apiLogout,
        apiUpdateProfile,
        apiChangePassword,
        apiVerifyPassword,
        apiDeleteAccount,
    } from "../lib/api.js";
    export let navigate;

    let activeTab = "profile";

    const tabs = [
        { id: "profile", label: "Profile", icon: "👤" },
        { id: "security", label: "Security", icon: "🔐" },
        { id: "privacy", label: "Privacy", icon: "🛡️" },
        { id: "admin", label: "Admin", icon: "👑" },
    ];

    // Form state
    let firstName = $user?.first_name || "";
    let lastName = $user?.last_name || "";
    let username = $user?.username || "";
    let email = $user?.email || "";
    let bio = $user?.bio || "";
    let borough = $user?.borough || "";

    let photoFile = null;
    let photoPreview = $user?.profile_picture || null;
    let fileInput;
    let removePhotoFlag = false;

    let isSaving = false;
    let message = "";
    let messageType = ""; // success or error

    // Validation errors for required fields
    let fieldErrors = { firstName: "", lastName: "", username: "" };

    // Security tab state
    let currentPassword = "";
    let newPassword = "";
    let confirmPassword = "";
    let isUpdatingPassword = false;
    let passwordVerificationStatus = null; // null, 'verifying', 'correct', 'incorrect'
    let verificationTimeout;
    let showSuccessModal = false;

    // Account Deletion
    let showDeleteModal = false;
    let deletePassword = "";
    let isDeleting = false;
    let deleteError = "";

    $: pwLong = newPassword.length >= 8;
    $: pwUpper = /[A-Z]/.test(newPassword);
    $: pwLower = /[a-z]/.test(newPassword);
    $: pwDigit = /[0-9]/.test(newPassword);

    function resetForm() {
        if (!$user) return;
        firstName = $user.first_name || "";
        lastName = $user.last_name || "";
        username = $user.username || "";
        email = $user.email || "";
        bio = $user.bio || "";
        borough = $user.borough || "";
        photoFile = null;
        photoPreview = $user.profile_picture || null;
        removePhotoFlag = false;
    }

    function cancelChanges() {
        resetForm();
        message = "Changes discarded.";
        messageType = "success";
        setTimeout(() => {
            if (message === "Changes discarded.") message = "";
        }, 2000);
    }

    let initialized = false;
    // Initialize form when user store is first populated
    $: if ($user && !initialized) {
        resetForm();
        initialized = true;
    }

    async function handleLogout() {
        await apiLogout();
        user.set(null);
        navigate("/login");
    }

    function handlePhotoClick() {
        fileInput.click();
    }

    function handleFileChange(e) {
        const file = e.target.files[0];
        if (file) {
            photoFile = file;
            removePhotoFlag = false;
            const reader = new FileReader();
            reader.onload = (e) => {
                photoPreview = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    async function handleRemovePhoto() {
        photoFile = null;
        photoPreview = null;
        removePhotoFlag = true;
    }

    async function saveChanges() {
        // Reset field errors
        fieldErrors = { firstName: "", lastName: "", username: "" };

        // Validate required fields
        let hasError = false;
        if (!firstName.trim()) {
            fieldErrors.firstName = "First name is required.";
            hasError = true;
        }
        if (!lastName.trim()) {
            fieldErrors.lastName = "Last name is required.";
            hasError = true;
        }
        if (!username.trim()) {
            fieldErrors.username = "Username is required.";
            hasError = true;
        }
        if (hasError) {
            message = "Please fill in all required fields.";
            messageType = "error";
            return;
        }

        isSaving = true;
        message = "";

        const formData = new FormData();
        formData.append("first_name", firstName);
        formData.append("last_name", lastName);
        formData.append("username", username);
        // email is immutable
        formData.append("bio", bio);
        formData.append("borough", borough);

        if (photoFile) {
            formData.append("profile_picture", photoFile);
        } else if (removePhotoFlag) {
            formData.append("remove_photo", "true");
        }

        try {
            const res = await apiUpdateProfile(formData);
            if (res.success) {
                user.set(res.user);
                message = "Profile updated successfully!";
                messageType = "success";
            } else {
                message = res.error || "An error occurred.";
                messageType = "error";
            }
        } catch (err) {
            message = "Failed to communicate with server.";
            messageType = "error";
        } finally {
            isSaving = false;
            // Clear message after 3 seconds
            setTimeout(() => {
                message = "";
            }, 3000);
        }
    }

    async function updatePassword() {
        if (!currentPassword || !newPassword || !confirmPassword) {
            message = "All password fields are required.";
            messageType = "error";
            return;
        }

        if (newPassword !== confirmPassword) {
            message = "New passwords do not match.";
            messageType = "error";
            return;
        }

        if (!pwLong || !pwUpper || !pwLower || !pwDigit) {
            message = "Password does not meet all security requirements.";
            messageType = "error";
            return;
        }

        isUpdatingPassword = true;
        message = "";

        try {
            const res = await apiChangePassword(
                currentPassword,
                newPassword,
                confirmPassword,
            );
            if (res.success) {
                showSuccessModal = true;
                currentPassword = "";
                newPassword = "";
                confirmPassword = "";
                passwordVerificationStatus = null;
            } else {
                message = res.error || "Failed to update password.";
                messageType = "error";
            }
        } catch (err) {
            message = "Failed to communicate with server.";
            messageType = "error";
        } finally {
            isUpdatingPassword = false;
            setTimeout(() => {
                if (message.includes("Password")) message = "";
            }, 3000);
        }
    }

    async function handleDeleteAccount() {
        if (!deletePassword) {
            deleteError = "Please enter your password to confirm.";
            return;
        }

        isDeleting = true;
        deleteError = "";

        try {
            const res = await apiDeleteAccount(deletePassword);
            if (res.success) {
                // Since this is a permanent deletion, we redirect to landing page
                user.set(null);
                navigate("/");
            } else {
                deleteError = res.error || "Failed to delete account.";
            }
        } catch (err) {
            deleteError = "Failed to communicate with server.";
        } finally {
            isDeleting = false;
        }
    }

    function checkPasswordRealtime(e) {
        const val = e.target.value;
        currentPassword = val;

        if (!val) {
            passwordVerificationStatus = null;
            return;
        }

        passwordVerificationStatus = "verifying";
        clearTimeout(verificationTimeout);

        verificationTimeout = setTimeout(async () => {
            try {
                const res = await apiVerifyPassword(val);
                if (res.success) {
                    passwordVerificationStatus = res.is_correct
                        ? "correct"
                        : "incorrect";
                }
            } catch (err) {
                passwordVerificationStatus = null;
            }
        }, 500); // 500ms debounce
    }
    import BackgroundRings from "../components/BackgroundRings.svelte";

    // Admin Stuff
    let adminAnswer = "";
    let adminMessage = "";
    let adminMessageType = "";

    async function submitAdminAnswer() {
        if (adminAnswer === "yEs i LOV3 trees") {
            const formData = new FormData();
            // We'll piggyback on the existing update-profile endpoint
            // but we need a dedicated endpoint — so call the API directly
            const res = await fetch("/api/become-admin/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.cookie.match(/csrftoken=([^;]+)/)?.[1] || "",
                },
                credentials: "include",
                body: JSON.stringify({ answer: adminAnswer }),
            });
            const data = await res.json();
            if (data.success) {
                user.update(u => ({ ...u, role: "admin" }));
                adminMessage = "👑 Welcome, Admin. Your power is immense.";
                adminMessageType = "success";
            } else {
                adminMessage = data.error || "Something went wrong.";
                adminMessageType = "error";
            }
        } else {
            adminMessage = "❌ Wrong answer. The trees do not recognize you.";
            adminMessageType = "error";
        }
        adminAnswer = "";
    }
</script>

<div class="page">
    <BackgroundRings />
    <LeftNav {navigate} activePage="settings" />

    <div class="settings-layout">
        <!-- Sidebar tabs -->
        <aside class="settings-sidebar">
            <h2 class="sidebar-title">⚙️ Settings</h2>
            <nav class="tab-list">
                {#each tabs as tab}
                    <button
                        class="tab-btn"
                        class:active={activeTab === tab.id}
                        on:click={() => (activeTab = tab.id)}
                    >
                        <span class="tab-icon">{tab.icon}</span>
                        <span class="tab-label">{tab.label}</span>
                    </button>
                {/each}
            </nav>

            <div class="sidebar-divider"></div>

            <button class="tab-btn danger" on:click={handleLogout}>
                <span class="tab-icon">↩</span>
                <span class="tab-label">Log Out</span>
            </button>
        </aside>

        <!-- Content area -->
        <main class="settings-content">
            {#if activeTab === "profile"}
                <div class="content-section">
                    <h3 class="section-title">Profile Information</h3>
                    <p class="section-desc">
                        Update your personal details and how others see you on
                        Treestagram.
                    </p>

                    {#if message}
                        <div class="alert alert-{messageType}">
                            {message}
                        </div>
                    {/if}

                    <div class="avatar-section">
                        <div class="avatar-circle">
                            {#if photoPreview}
                                <img
                                    src={photoPreview}
                                    alt="Profile"
                                    class="preview-img"
                                />
                            {:else}
                                🌿
                            {/if}
                        </div>
                        <input
                            type="file"
                            accept="image/*"
                            style="display: none;"
                            bind:this={fileInput}
                            on:change={handleFileChange}
                        />
                        <div class="avatar-actions">
                            <button
                                class="btn-secondary"
                                on:click={handlePhotoClick}>Change Photo</button
                            >
                            <button
                                class="btn-ghost"
                                on:click={handleRemovePhoto}>Remove</button
                            >
                        </div>
                    </div>

                    <div class="form-row-2">
                        <div class="form-group" class:has-error={fieldErrors.firstName}>
                            <label for="first-name">First Name <span class="required">*</span></label>
                            <input
                                id="first-name"
                                type="text"
                                bind:value={firstName}
                                placeholder="Jane"
                                class:input-error={fieldErrors.firstName}
                                on:input={() => fieldErrors.firstName = ""}
                            />
                            {#if fieldErrors.firstName}
                                <p class="field-error">{fieldErrors.firstName}</p>
                            {/if}
                        </div>
                        <div class="form-group" class:has-error={fieldErrors.lastName}>
                            <label for="last-name">Last Name <span class="required">*</span></label>
                            <input
                                id="last-name"
                                type="text"
                                bind:value={lastName}
                                placeholder="Doe"
                                class:input-error={fieldErrors.lastName}
                                on:input={() => fieldErrors.lastName = ""}
                            />
                            {#if fieldErrors.lastName}
                                <p class="field-error">{fieldErrors.lastName}</p>
                            {/if}
                        </div>
                    </div>

                    <div class="form-group" class:has-error={fieldErrors.username}>
                        <label for="username">Username <span class="required">*</span></label>
                        <input
                            id="username"
                            type="text"
                            bind:value={username}
                            placeholder="tree_guardian"
                            class:input-error={fieldErrors.username}
                            on:input={() => fieldErrors.username = ""}
                        />
                        {#if fieldErrors.username}
                            <p class="field-error">{fieldErrors.username}</p>
                        {/if}
                    </div>

                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            bind:value={email}
                            readonly
                            placeholder="you@example.com"
                            class="immutable-field"
                        />
                        <p class="field-hint">
                            Email address cannot be changed.
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="bio">Bio</label>
                        <textarea
                            id="bio"
                            rows="3"
                            bind:value={bio}
                            placeholder="Tell us about your love for NYC trees…"
                        ></textarea>
                    </div>

                    <div class="form-group">
                        <label for="borough">Borough</label>
                        <select id="borough" bind:value={borough}>
                            <option value="Manhattan">Manhattan</option>
                            <option value="Brooklyn">Brooklyn</option>
                            <option value="Queens">Queens</option>
                            <option value="Bronx">Bronx</option>
                            <option value="Staten Island">Staten Island</option>
                        </select>
                    </div>

                    <div class="form-actions">
                        <button
                            class="btn-primary"
                            on:click={saveChanges}
                            disabled={isSaving}
                        >
                            {isSaving ? "Saving..." : "Save Changes"}
                        </button>
                        <button class="btn-ghost" on:click={cancelChanges}
                            >Cancel</button
                        >
                    </div>
                </div>
            {:else if activeTab === "security"}
                <div class="content-section">
                    <h3 class="section-title">Security</h3>
                    <p class="section-desc">
                        Manage your password and account security settings.
                    </p>

                    <div class="security-card">
                        <div class="security-card-header">
                            <div>
                                <h4>Change Password</h4>
                                <p>
                                    Update your password regularly to keep your
                                    account secure.
                                </p>
                            </div>
                        </div>

                        <div class="form-group password-verification-wrapper">
                            <label for="current-pw">Current Password</label>
                            <div class="input-with-icon">
                                <input
                                    id="current-pw"
                                    type="password"
                                    value={currentPassword}
                                    on:input={checkPasswordRealtime}
                                    placeholder="••••••••"
                                    class:status-correct={passwordVerificationStatus ===
                                        "correct"}
                                    class:status-incorrect={passwordVerificationStatus ===
                                        "incorrect"}
                                />
                                <div class="verification-icon">
                                    {#if passwordVerificationStatus === "verifying"}
                                        <span class="spinner-sm"></span>
                                    {:else if passwordVerificationStatus === "correct"}
                                        <span class="icon-success">✔️</span>
                                    {:else if passwordVerificationStatus === "incorrect"}
                                        <span class="icon-error">❌</span>
                                    {/if}
                                </div>
                            </div>
                            {#if passwordVerificationStatus === "incorrect"}
                                <p class="field-error">
                                    Current password is incorrect.
                                </p>
                            {/if}
                        </div>
                        <div class="form-group">
                            <label for="new-pw">New Password</label>
                            <input
                                id="new-pw"
                                type="password"
                                bind:value={newPassword}
                                placeholder="min 8 characters"
                            />
                            {#if newPassword.length > 0}
                                <div class="pw-rules">
                                    <div class="pw-rule" class:met={pwLong}>
                                        {pwLong ? "✓" : "○"} At least 8 characters
                                    </div>
                                    <div class="pw-rule" class:met={pwUpper}>
                                        {pwUpper ? "✓" : "○"} One uppercase letter
                                    </div>
                                    <div class="pw-rule" class:met={pwLower}>
                                        {pwLower ? "✓" : "○"} One lowercase letter
                                    </div>
                                    <div class="pw-rule" class:met={pwDigit}>
                                        {pwDigit ? "✓" : "○"} One number
                                    </div>
                                </div>
                            {/if}
                        </div>
                        <div class="form-group">
                            <label for="confirm-pw">Confirm New Password</label>
                            <input
                                id="confirm-pw"
                                type="password"
                                bind:value={confirmPassword}
                                placeholder="••••••••"
                            />
                            {#if confirmPassword && newPassword !== confirmPassword}
                                <small class="match-hint no-match"
                                    >✗ Passwords don't match</small
                                >
                            {:else if confirmPassword && newPassword === confirmPassword}
                                <small class="match-hint match"
                                    >✓ Passwords match</small
                                >
                            {/if}
                        </div>
                        <button
                            class="btn-primary"
                            on:click={updatePassword}
                            disabled={isUpdatingPassword}
                        >
                            {isUpdatingPassword
                                ? "Updating..."
                                : "Update Password"}
                        </button>
                    </div>

                    <div class="security-card">
                        <div class="security-card-header">
                            <div>
                                <h4>Two-Factor Authentication</h4>
                                <p>
                                    Add an extra layer of security to your
                                    account.
                                </p>
                            </div>
                            <span class="badge badge-off">Off</span>
                        </div>
                        <button class="btn-secondary">Enable 2FA</button>
                    </div>

                    <div class="security-card">
                        <div class="security-card-header">
                            <div>
                                <h4>Active Sessions</h4>
                                <p>
                                    Manage devices where you're currently logged
                                    in.
                                </p>
                            </div>
                        </div>
                        <div class="session-item">
                            <span class="session-icon">💻</span>
                            <div class="session-info">
                                <strong>This device</strong>
                                <small>Last active: Now</small>
                            </div>
                            <span class="badge badge-active">Active</span>
                        </div>
                    </div>

                    <div class="danger-zone">
                        <h4>⚠️ Danger Zone</h4>
                        <p>
                            Permanently delete your account and all associated
                            data. This action cannot be undone.
                        </p>
                        <button
                            class="btn-danger"
                            on:click={() => (showDeleteModal = true)}
                        >
                            Delete Account
                        </button>
                    </div>
                </div>
            {:else if activeTab === "privacy"}
                <div class="content-section">
                    <h3 class="section-title">Privacy</h3>
                    <p class="section-desc">
                        Control who can see your profile and activity.
                    </p>

                    <div class="toggle-card">
                        <div class="toggle-info">
                            <h4>Private Profile</h4>
                            <p>
                                When enabled, only approved followers can see
                                your posts and tree observations.
                            </p>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="toggle-card">
                        <div class="toggle-info">
                            <h4>Show Activity Status</h4>
                            <p>
                                Let others see when you were last active on
                                Treestagram.
                            </p>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" checked />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="toggle-card">
                        <div class="toggle-info">
                            <h4>Show Borough</h4>
                            <p>Display your borough on your public profile.</p>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" checked />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="toggle-card">
                        <div class="toggle-info">
                            <h4>Allow Group Chat Invites</h4>
                            <p>Let other users add you to tree group chats.</p>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" checked />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>

                    <div class="form-actions">
                        <button class="btn-primary"
                            >Save Privacy Settings</button
                        >
                    </div>
                </div>
            {:else if activeTab === "admin"}
                <div class="content-section">
                    <h3 class="section-title">👑 Admin Access</h3>
                    <p class="section-desc">Answer the sacred question to claim your throne.</p>

                    <div class="form-group">
                        <label for="admin-question">Are thou an admin?</label>
                        <input
                            id="admin-question"
                            type="text"
                            bind:value={adminAnswer}
                            placeholder="Speak thy truth…"
                        />
                    </div>

                    {#if adminMessage}
                        <div class="alert alert-{adminMessageType}">{adminMessage}</div>
                    {/if}

                    <div class="form-actions">
                        <button class="btn-primary" on:click={submitAdminAnswer}>
                            Submit
                        </button>
                    </div>
                </div>
            {/if}
        </main>
    </div>
</div>

{#if showSuccessModal}
    <button
        class="modal-backdrop"
        on:click={() => (showSuccessModal = false)}
        on:keydown={(e) => e.key === "Escape" && (showSuccessModal = false)}
        aria-label="Close modal"
    >
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <div
            class="success-modal"
            on:click|stopPropagation
            on:keydown|stopPropagation
            role="dialog"
            aria-modal="true"
        >
            <div class="modal-icon">🌳</div>
            <h3>Updated!</h3>
            <p>Your password has been changed successfully.</p>
            <button
                class="btn-primary"
                on:click={() => (showSuccessModal = false)}>Continue</button
            >
        </div>
    </button>
{/if}

{#if showDeleteModal}
    <button
        class="modal-backdrop"
        on:click={() => (showDeleteModal = false)}
        on:keydown={(e) => e.key === "Escape" && (showDeleteModal = false)}
        aria-label="Close delete confirmation"
    >
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <div
            class="delete-modal"
            on:click|stopPropagation
            on:keydown|stopPropagation
            role="dialog"
            aria-modal="true"
        >
            <div class="modal-icon">⚠️</div>
            <h3>Delete Account?</h3>
            <p>
                This action is <strong>permanent</strong>. Your data will be
                sent to the compost pile of history.
            </p>

            <div
                class="form-group"
                style="text-align: left; margin-top: 1.5rem;"
            >
                <label for="delete-pw">Confirm with Password</label>
                <input
                    id="delete-pw"
                    type="password"
                    bind:value={deletePassword}
                    placeholder="Enter your password"
                    on:keydown={(e) =>
                        e.key === "Enter" && handleDeleteAccount()}
                    on:click|stopPropagation
                />
                {#if deleteError}
                    <p class="field-error">{deleteError}</p>
                {/if}
            </div>

            <div class="modal-actions">
                <button
                    class="btn-ghost"
                    on:click={() => {
                        showDeleteModal = false;
                        deletePassword = "";
                        deleteError = "";
                    }}>Cancel</button
                >
                <button
                    class="btn-danger-filled"
                    on:click={handleDeleteAccount}
                    disabled={isDeleting}
                >
                    {#if isDeleting}
                        Deleting...
                    {:else}
                        Delete Permanently
                    {/if}
                </button>
            </div>
        </div>
    </button>
{/if}

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
        --shadow: rgba(44, 24, 16, 0.1);
    }

    .page {
        min-height: 100vh;
        background: #faf9f6; /* Warm White Background */
        font-family: var(--t-font-body);
        color: #4a4a4a; /* Dark gray for contrast on light background */
        position: relative;
        z-index: 0;
        overflow: hidden;
        padding-left: 60px;
    }
    /* ── Layout ────────────────────────────────────────────────── */
    .settings-layout {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        display: grid;
        grid-template-columns: 240px 1fr;
        gap: 2rem;
    }

    /* ── Sidebar ───────────────────────────────────────────────── */
    .settings-sidebar {
        position: sticky;
        top: 2rem;
        align-self: start;
        z-index: 10;
        background: #cdd9af; /* Sage Mist sidebar */
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(164, 74, 63, 0.15); /* Subtle Redwood border */
        box-shadow: 0 8px 32px rgba(138, 154, 91, 0.08);
    }
    .sidebar-title {
        font-family: "Playfair Display", serif;
        font-size: 1.4rem;
        color: #a44a3f; /* Terracotta Clay title */
        margin-bottom: 1.2rem;
        padding-left: 0.5rem;
    }
    .tab-list {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .tab-btn {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.7rem 0.9rem;
        background: none;
        border: none;
        border-radius: 10px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        color: #a44a3f; /* Terracotta Clay labels */
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
        width: 100%;
    }
    .tab-btn:hover {
        background: rgba(180, 138, 61, 0.1);
        color: #d4a853;
    }
    .tab-btn.active {
        background: #36454f; /* Charcoal Gray active tab */
        color: #faf9f6; /* Contrasting text */
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(138, 154, 91, 0.15);
    }
    .tab-btn.danger {
        color: #b91c1c;
    }
    .tab-btn.danger:hover {
        background: rgba(185, 28, 28, 0.08);
    }
    .tab-icon {
        font-size: 1rem;
        width: 20px;
        text-align: center;
        flex-shrink: 0;
    }
    .sidebar-divider {
        height: 1px;
        background: rgba(205, 133, 63, 0.3); /* Terracotta divider */
        margin: 0.8rem 0;
    }

    /* ── Content Area ──────────────────────────────────────────── */
    .settings-content {
        min-width: 0;
    }
    .content-section {
        background: #cdd9af; /* Lighter Sage Mist content card */
        border: 1px solid rgba(164, 74, 63, 0.15); /* Subtle Redwood border */
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(138, 154, 91, 0.08);
        padding: 2rem;
        color: #2b2b2b; /* Contrast text for lighter background */
    }
    .section-title {
        font-family: "Playfair Display", serif;
        font-size: 1.5rem;
        color: #a44a3f; /* Terracotta Clay title */
        margin-bottom: 0.3rem;
    }
    .section-desc {
        color: rgba(43, 43, 43, 0.7); /* Muted dark text for light background */
        font-size: 0.88rem;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* ── Avatar ────────────────────────────────────────────────── */
    .avatar-section {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        margin-bottom: 2rem;
        padding-bottom: 2rem;
        border-bottom: 1px solid var(--mist);
    }
    .avatar-circle {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        flex-shrink: 0;
        overflow: hidden;
    }
    .preview-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .avatar-actions {
        display: flex;
        gap: 0.5rem;
    }

    .alert {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .alert-success {
        background: rgba(61, 90, 62, 0.1);
        color: #3d5a3e;
        border: 1px solid rgba(61, 90, 62, 0.2);
    }
    .alert-error {
        background: rgba(185, 28, 28, 0.05);
        color: #b91c1c;
        border: 1px solid rgba(185, 28, 28, 0.1);
    }

    /* ── Form Elements ─────────────────────────────────────────── */
    .form-row-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    .form-group {
        margin-bottom: 1.2rem;
    }
    .form-group label {
        display: block;
        font-size: 0.78rem;
        font-weight: 600;
        color: #a44a3f; /* Terracotta Clay form labels */
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .form-group input,
    .form-group textarea,
    .form-group select {
        width: 100%;
        background: #ffffff;
        border: 1.5px solid var(--t-border);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-family: var(--t-font-body);
        font-size: 0.95rem;
        color: var(--bark);
        transition: all 0.2s;
        outline: none;
    }
    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
        border-color: var(--t-status-fair);
        background: #fffef7;
        box-shadow: 0 0 0 3px rgba(212, 168, 83, 0.1);
    }
    .form-group textarea {
        resize: vertical;
        min-height: 80px;
    }
    .form-group select {
        cursor: pointer;
    }

    .form-actions {
        display: flex;
        gap: 0.8rem;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--mist);
    }

    /* ── Buttons ───────────────────────────────────────────────── */
    .btn-primary {
        padding: 0.75rem 1.8rem;
        background: #36454f; /* Charcoal Gray button */
        color: #faf9f6; /* Contrasting text */
        border: none;
        border-radius: 12px;
        font-family: var(--t-font-body);
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(138, 154, 91, 0.1);
    }
    .btn-primary:hover {
        background: #b8c1b5;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(138, 154, 91, 0.2);
    }

    /* Verification Styles */
    .input-with-icon {
        position: relative;
        display: flex;
        align-items: center;
    }
    .input-with-icon input {
        width: 100%;
        padding-right: 40px;
    }
    .verification-icon {
        position: absolute;
        right: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }
    .icon-success {
        color: #8a9a5b;
    }
    .icon-error {
        color: #a44a3f;
    }

    .status-correct {
        border-color: #8a9a5b !important;
        background: rgba(138, 154, 91, 0.05) !important;
    }
    .status-incorrect {
        border-color: #a44a3f !important;
        background: rgba(164, 74, 63, 0.05) !important;
    }
    .field-error {
        font-size: 0.72rem;
        color: #a44a3f;
        margin-top: 4px;
        font-weight: 500;
    }
    .input-error {
        border-color: #b91c1c !important;
        background: rgba(185, 28, 28, 0.03) !important;
    }
    .input-error:focus {
        box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.1) !important;
    }
    .required {
        color: #b91c1c;
        font-weight: 700;
    }

    .match-hint {
        display: block;
        font-size: 0.72rem;
        margin-top: 0.4rem;
        font-weight: 500;
    }
    .match-hint.no-match {
        color: #a44a3f;
    }
    .match-hint.match {
        color: #8a9a5b;
    }

    .spinner-sm {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(138, 154, 91, 0.2);
        border-top: 2px solid #8a9a5b;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    .immutable-field {
        background: #f0f0f0 !important;
        cursor: not-allowed;
        color: #666 !important;
        border-color: #ddd !important;
    }
    .field-hint {
        font-size: 0.72rem;
        color: #a44a3f;
        margin-top: 4px;
        opacity: 0.8;
    }
    .btn-secondary {
        padding: 0.65rem 1.4rem;
        background: white;
        border: 1.5px solid var(--t-status-good);
        border-radius: 12px;
        color: var(--t-status-good);
        font-family: var(--t-font-body);
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-secondary:hover {
        background: rgba(61, 90, 62, 0.05);
        color: #2d482e;
        border-color: #2d482e;
    }
    .btn-ghost {
        padding: 0.6rem 1.2rem;
        background: none;
        border: none;
        color: var(--sage);
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        cursor: pointer;
        transition: color 0.2s;
    }
    .btn-ghost:hover {
        color: var(--moss);
    }
    .btn-danger {
        padding: 0.65rem 1.3rem;
        background: none;
        border: 1.5px solid #e57373;
        border-radius: 10px;
        color: #b91c1c;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-danger:hover {
        background: rgba(185, 28, 28, 0.06);
    }

    /* ── Security Cards ────────────────────────────────────────── */
    .security-card {
        border: 1px solid var(--mist);
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
    }
    .security-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .security-card-header h4,
    .toggle-info h4,
    .notif-group h4,
    .danger-zone h4,
    .session-info strong {
        font-size: 0.95rem;
        color: #a44a3f; /* Terracotta Clay universal labels */
        margin-bottom: 0.2rem;
    }
    .security-card-header p {
        font-size: 0.82rem;
        color: var(--sage);
        line-height: 1.4;
    }
    .badge {
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        flex-shrink: 0;
    }
    .badge-off {
        background: rgba(185, 28, 28, 0.1);
        color: #b91c1c;
    }
    .badge-active {
        background: rgba(61, 90, 62, 0.15);
        color: var(--moss);
    }

    /* Password Rules */
    .pw-rules {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.15rem 0.8rem;
        margin-top: 0.6rem;
        background: rgba(255, 255, 255, 0.4);
        padding: 0.6rem;
        border-radius: 8px;
        border: 1px solid var(--t-border);
    }
    .pw-rule {
        font-size: 0.72rem;
        color: var(--sage);
        transition: color 0.2s;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .pw-rule.met {
        color: var(--t-status-good);
        font-weight: 600;
    }
    .session-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.6rem 0;
    }
    .session-icon {
        font-size: 1.3rem;
    }
    .session-info {
        flex: 1;
    }
    .session-info strong {
        display: block;
        font-size: 0.85rem;
        color: var(--ink);
    }
    .session-info small {
        font-size: 0.75rem;
        color: var(--sage);
    }

    .danger-zone {
        margin-top: 2rem;
        padding: 1.4rem;
        border: 1.5px solid #e57373;
        border-radius: 12px;
        background: rgba(185, 28, 28, 0.03);
    }
    .danger-zone h4 {
        font-size: 0.95rem;
        color: #b91c1c;
        margin-bottom: 0.4rem;
    }
    .danger-zone p {
        font-size: 0.82rem;
        color: var(--sage);
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* ── Toggle Cards ──────────────────────────────────────────── */
    .toggle-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border: 1px solid var(--mist);
        border-radius: 12px;
        margin-bottom: 0.6rem;
        gap: 1rem;
    }
    .toggle-info h4 {
        font-size: 0.9rem;
        color: #b48a3d;
        margin-bottom: 0.15rem;
    }
    .toggle-info p {
        font-size: 0.78rem;
        color: var(--sage);
        line-height: 1.4;
    }

    /* Toggle Switch */
    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 44px;
        height: 24px;
        flex-shrink: 0;
    }
    .toggle-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    .toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--canopy);
        border-radius: 24px;
        transition: background 0.3s;
    }
    .toggle-slider::before {
        content: "";
        position: absolute;
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background: white;
        border-radius: 50%;
        transition: transform 0.3s;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
    }
    .toggle-switch input:checked + .toggle-slider {
        background: var(--moss);
    }
    .toggle-switch input:checked + .toggle-slider::before {
        transform: translateX(20px);
    }

    /* ── Notifications ─────────────────────────────────────────── */
    .notif-group {
        margin-bottom: 1.5rem;
    }
    .notif-group > h4 {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
        margin-bottom: 0.6rem;
        padding-left: 0.2rem;
    }

    /* ── Success Modal ─────────────────────────────────────────── */
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(44, 24, 16, 0.4);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
        animation: fadeIn 0.3s ease;
        border: none;
        width: 100%;
        height: 100%;
        cursor: default;
    }
    .success-modal {
        background: white;
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
        animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .modal-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    .success-modal h3 {
        color: var(--bark);
        font-family: "Playfair Display", serif;
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
    }
    .success-modal p {
        color: var(--sage);
        font-size: 1rem;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    @keyframes slideUp {
        from {
            transform: translateY(40px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .delete-modal {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        text-align: center;
        max-width: 440px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(185, 28, 28, 0.2);
        animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .delete-modal h3 {
        color: #b91c1c;
        font-family: "Playfair Display", serif;
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
    }
    .delete-modal strong {
        color: #b91c1c;
    }
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }
    .btn-danger-filled {
        padding: 0.75rem 1.5rem;
        background: #b91c1c;
        color: white;
        border: none;
        border-radius: 12px;
        font-family: var(--t-font-body);
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-danger-filled:hover:not(:disabled) {
        background: #991b1b;
        transform: translateY(-2px);
    }
    .btn-danger-filled:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
</style>
