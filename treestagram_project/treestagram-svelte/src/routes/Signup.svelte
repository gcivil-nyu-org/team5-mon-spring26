<script>
  import { onMount } from 'svelte'
  import { user, apiSignup } from '../lib/api.js'

  export let navigate

  let step = 1
  let mounted = false
  let loading = false
  let error = ''
  let focused = ''
  let shake = false
  let showPassword = false;

  // Form fields
  let firstName = '', lastName = '', email = ''
  let username = '', borough = '', password = '', confirmPassword = ''

  const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']

  onMount(() => setTimeout(() => mounted = true, 50))

  function triggerShake(msg) {
    error = msg; shake = true
    setTimeout(() => shake = false, 600)
  }

  function nextStep() {
    error = ''
    if (step === 1) {
      if (!email) return triggerShake('Email is required.')
      if (!email.includes('@')) return triggerShake('Enter a valid email.')
      step = 2
    } else if (step === 2) {
      if (!username) return triggerShake('Choose a username.')
      if (username.length < 3) return triggerShake('Username must be at least 3 characters.')
      step = 3
    }
  }

  function prevStep() {
    error = ''
    step = Math.max(1, step - 1)
  }

  async function handleSignup() {
    error = ''
    if (!password) return triggerShake('Password is required.')
    if (password.length < 8) return triggerShake('Password must be at least 8 characters.')
    if (password !== confirmPassword) return triggerShake('Passwords do not match.')

    loading = true
    try {
      const data = await apiSignup({
        first_name: firstName,
        last_name: lastName,
        email,
        username,
        borough,
        password1: password,
        password2: confirmPassword,
      })
      if (data.success) {
        user.set(data.user)
        navigate('/home')
      } else {
        const errs = data.errors || {}
        const first = Object.values(errs)[0]
        triggerShake(Array.isArray(first) ? first[0] : (data.error || 'Signup failed.'))
      }
    } catch {
      triggerShake('Could not connect to server.')
    }
    loading = false
  }

  function handleKey(e) {
    if (e.key === 'Enter') {
      if (step < 3) nextStep()
      else handleSignup()
    }
  }

  $: progress = ((step - 1) / 2) * 100
  $: stepLabels = ['Identity', 'Profile', 'Security']
</script>

<div class="page" class:mounted>
  <!-- Forest bg (reused) -->
  <div class="forest-bg">
    <div class="layer layer-1"></div>
    <div class="layer layer-2"></div>
    <div class="fireflies">
      {#each Array(8) as _, i}
        <span class="firefly" style="
          --x:{8+i*11}%;--y:{20+(i%4)*18}%;
          --delay:{i*0.5}s;--dur:{2.8+(i%3)*0.6}s;
        "></span>
      {/each}
    </div>
  </div>

  <div class="card" class:shake>
    <div class="card-inner">

      <!-- Brand header -->
      <div class="brand">
        <span class="logo-tree">🌱</span>
        <div>
          <h1>Join Treestagram</h1>
          <p class="tagline">Plant your roots in NYC</p>
        </div>
      </div>

      <!-- Step progress -->
      <div class="steps">
        {#each stepLabels as label, i}
          <div class="step-item" class:done={step > i+1} class:active={step === i+1}>
            <div class="step-dot">
              {#if step > i+1}✓{:else}{i+1}{/if}
            </div>
            <span class="step-label">{label}</span>
          </div>
          {#if i < 2}
            <div class="step-line" class:filled={step > i+1}></div>
          {/if}
        {/each}
      </div>

      <!-- Step 1: Identity -->
      {#if step === 1}
        <div class="form-step" role="group" on:keydown={handleKey}>
          <div class="row-2">
            <div class="field" class:focused={focused==='firstName'}>
              <label>🌿 First name</label>
              <input type="text" placeholder="Ada" bind:value={firstName}
                on:focus={()=>focused='firstName'} on:blur={()=>focused=''} />
              <div class="field-line"></div>
            </div>
            <div class="field" class:focused={focused==='lastName'}>
              <label>🌿 Last name</label>
              <input type="text" placeholder="Lovelace" bind:value={lastName}
                on:focus={()=>focused='lastName'} on:blur={()=>focused=''} />
              <div class="field-line"></div>
            </div>
          </div>
          <div class="field" class:focused={focused==='email'}>
            <label>📧 Email address</label>
            <input type="email" placeholder="you@example.com" bind:value={email}
              on:focus={()=>focused='email'} on:blur={()=>focused=''} />
            <div class="field-line"></div>
          </div>
        </div>

      <!-- Step 2: Profile -->
      {:else if step === 2}
        <div class="form-step" role="group" on:keydown={handleKey}>
          <div class="field" class:focused={focused==='username'}>
            <label>🪵 Username</label>
            <input type="text" placeholder="tree_guardian" bind:value={username}
              on:focus={()=>focused='username'} on:blur={()=>focused=''} />
            <div class="field-line"></div>
          </div>
          <div class="field">
            <label>📍 Your borough</label>
            <div class="borough-grid">
              {#each boroughs as b}
                <button
                  class="borough-btn"
                  class:selected={borough === b}
                  on:click={() => borough = borough === b ? '' : b}
                  type="button"
                >
                  {b === 'Manhattan' ? '🗽' : b === 'Brooklyn' ? '🌉' : b === 'Queens' ? '✈️' : b === 'Bronx' ? '🌿' : '⛴️'}
                  {b}
                </button>
              {/each}
            </div>
          </div>
        </div>

      <!-- Step 3: Security -->
      {:else}
        <div class="form-step" role="group" on:keydown={handleKey}>
          <div class="field" class:focused={focused==='pass'}>
            <label>🔑 Password</label>
            <div class="input-container">
              <input 
                type={showPassword ? 'text' : 'password'} 
                placeholder="min 8 characters" 
                value={password}
                on:input={(e) => password = e.target.value}
                on:focus={()=>focused='pass'} 
                on:blur={()=>focused=''} 
              />
              <button 
                type="button" 
                class="toggle-visibility" 
                on:click={() => showPassword = !showPassword}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <div class="field-line"></div>
          </div>

          <div class="strength-bar">
            <div class="strength-fill" style="width:{Math.min(100,(password.length/12)*100)}%;
              background:{password.length < 6 ? '#e74c3c' : password.length < 10 ? '#f39c12' : '#52b788'}">
            </div>
          </div>

          <div class="field" class:focused={focused==='confirm'}>
            <label>🔒 Confirm password</label>
            <div class="input-container">
              <input 
                type={showPassword ? 'text' : 'password'} 
                placeholder="••••••••" 
                value={confirmPassword}
                on:input={(e) => confirmPassword = e.target.value}
                on:focus={()=>focused='confirm'} 
                on:blur={()=>focused=''} 
              />
              <button 
                type="button" 
                class="toggle-visibility" 
                on:click={() => showPassword = !showPassword}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <div class="field-line"></div>
            
            {#if confirmPassword && password !== confirmPassword}
              <span class="match-hint mismatch">✗ Passwords don't match</span>
            {:else if confirmPassword && password === confirmPassword}
              <span class="match-hint match">✓ Passwords match</span>
            {/if}
          </div>
        </div>
      {/if}

      {#if error}
        <div class="error-msg">⚠️ {error}</div>
      {/if}

      <!-- Nav buttons -->
      <div class="btn-row">
        {#if step > 1}
          <button class="btn-back" on:click={prevStep} type="button">← Back</button>
        {/if}
        {#if step < 3}
          <button class="btn-next" on:click={nextStep} type="button">
            Continue →
          </button>
        {:else}
          <button class="btn-next" on:click={handleSignup} disabled={loading} type="button">
            {#if loading}
              <span class="spinner"></span> Growing…
            {:else}
              Grow your account 🌳
            {/if}
          </button>
        {/if}
      </div>

      <div class="footer">
        Already a member?
        <button class="link-btn" on:click={() => navigate('/login')}>Log in →</button>
      </div>
    </div>
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    position: relative;
    overflow: hidden;
    background: linear-gradient(160deg, #071410 0%, #0d2318 40%, #0a1c12 100%);
  }
  .forest-bg { position: absolute; inset: 0; pointer-events: none; }
  .layer { position: absolute; bottom: 0; width: 100%; background-repeat: repeat-x; }
  .layer-1 {
    height: 200px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 200'%3E%3Cpath d='M0,160 Q60,100 120,145 Q180,85 240,130 Q300,70 360,115 Q420,55 480,100 Q540,75 600,120 Q660,60 720,110 Q780,80 840,125 Q900,65 960,110 Q1020,85 1080,130 Q1140,75 1200,115 L1200,200 L0,200Z' fill='%23122d1e'/%3E%3C/svg%3E");
    background-size: 1200px 200px;
    animation: sway 16s ease-in-out infinite alternate;
  }
  .layer-2 {
    height: 120px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120'%3E%3Cpath d='M0,90 Q100,50 200,80 Q300,35 400,70 Q500,40 600,75 Q700,45 800,78 Q900,42 1000,72 Q1100,50 1200,75 L1200,120 L0,120Z' fill='%231a3d27'/%3E%3C/svg%3E");
    background-size: 1200px 120px;
    animation: sway 10s ease-in-out infinite alternate-reverse;
  }
  .fireflies { position: absolute; inset: 0; }
  .firefly {
    position: absolute; left: var(--x); top: var(--y);
    width: 4px; height: 4px; border-radius: 50%;
    background: #a8f5b0; box-shadow: 0 0 6px 2px rgba(168,245,176,.6);
    animation: float var(--dur) var(--delay) ease-in-out infinite alternate;
  }
  @keyframes float {
    0%   { opacity: 0; transform: translate(0,0); }
    30%  { opacity: 1; }
    100% { opacity: 0; transform: translate(18px,-28px); }
  }
  @keyframes sway {
    from { transform: translateX(0); }
    to   { transform: translateX(-25px); }
  }

  /* Card */
  .card {
    position: relative; z-index: 10;
    width: 100%; max-width: 460px;
    background: rgba(10,28,18,.78);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(82,183,136,.18);
    border-radius: 24px;
    box-shadow: 0 32px 64px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.06);
    opacity: 0; transform: translateY(24px);
    transition: opacity .5s, transform .5s;
  }

  .input-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .input-container input {
    width: 100%;
    padding-right: 2.5rem; 
  }

  .toggle-visibility {
    position: absolute;
    right: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .toggle-visibility:hover {
    opacity: 1;
  }

  .page.mounted .card { opacity: 1; transform: translateY(0); }
  .card.shake { animation: shake .5s; }
  @keyframes shake {
    0%,100%{transform:translateX(0)} 15%{transform:translateX(-10px)}
    30%{transform:translateX(9px)} 45%{transform:translateX(-7px)}
    60%{transform:translateX(5px)} 75%{transform:translateX(-3px)}
  }
  .card-inner { padding: 2.4rem 2.4rem 2rem; }

  /* Brand */
  .brand {
    display: flex; align-items: center; gap: 14px; margin-bottom: 1.8rem;
  }
  .logo-tree { font-size: 2.5rem; filter: drop-shadow(0 0 10px rgba(82,183,136,.5)); }
  h1 {
    font-family: 'Playfair Display', serif; font-size: 1.7rem;
    font-weight: 900; color: #d4f5dd; line-height: 1.1; margin-bottom: 2px;
  }
  .tagline { font-size: .78rem; color: rgba(168,220,180,.5); letter-spacing: 1.5px; text-transform: uppercase; }

  /* Step progress */
  .steps {
    display: flex; align-items: center; margin-bottom: 1.8rem;
  }
  .step-item { display: flex; align-items: center; gap: 6px; }
  .step-dot {
    width: 26px; height: 26px; border-radius: 50%;
    background: rgba(255,255,255,.07); border: 1.5px solid rgba(82,183,136,.25);
    display: flex; align-items: center; justify-content: center;
    font-size: .75rem; font-weight: 700; color: rgba(255,255,255,.3);
    transition: all .3s;
  }
  .step-item.active .step-dot {
    background: #2d6a4f; border-color: #52b788; color: #d4f5dd;
    box-shadow: 0 0 12px rgba(82,183,136,.35);
  }
  .step-item.done .step-dot {
    background: #52b788; border-color: #52b788; color: #071410;
  }
  .step-label { font-size: .72rem; color: rgba(168,220,180,.4); text-transform: uppercase; letter-spacing: 1px; }
  .step-item.active .step-label { color: #95d5b2; }
  .step-item.done .step-label { color: #52b788; }
  .step-line {
    flex: 1; height: 1.5px; background: rgba(82,183,136,.15); margin: 0 8px;
    transition: background .4s;
  }
  .step-line.filled { background: #52b788; }

  /* Form step */
  .form-step { display: flex; flex-direction: column; gap: 1.1rem; min-height: 160px; }
  .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }

  .field { position: relative; }
  label {
    display: flex; align-items: center; gap: 5px;
    font-size: .72rem; font-weight: 600;
    color: rgba(168,220,180,.45); letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 7px; transition: color .2s;
  }
  .field.focused label { color: #52b788; }
  input {
    width: 100%;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(82,183,136,.15);
    border-radius: 10px; padding: 12px 15px;
    font-size: .93rem; font-family: 'DM Sans', sans-serif;
    color: #d4f5dd; outline: none;
    transition: border-color .25s, background .25s, box-shadow .25s;
  }
  input::placeholder { color: rgba(255,255,255,.18); }
  input:focus {
    border-color: rgba(82,183,136,.5);
    background: rgba(82,183,136,.06);
    box-shadow: 0 0 0 3px rgba(82,183,136,.1);
  }
  .field-line {
    position: absolute; bottom: 0; left: 15px; right: 15px;
    height: 1.5px; background: #52b788; transform: scaleX(0);
    transform-origin: left; transition: transform .3s; border-radius: 1px;
  }
  .field.focused .field-line { transform: scaleX(1); }

  /* Borough grid */
  .borough-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
  }
  .borough-btn {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(82,183,136,.15);
    border-radius: 9px; padding: 9px 4px;
    color: rgba(168,220,180,.6); font-size: .78rem;
    font-family: 'DM Sans', sans-serif; cursor: pointer;
    transition: all .2s; text-align: center;
    display: flex; flex-direction: column; align-items: center; gap: 3px;
  }
  .borough-btn:hover { background: rgba(82,183,136,.1); border-color: rgba(82,183,136,.35); color: #95d5b2; }
  .borough-btn.selected {
    background: rgba(82,183,136,.18); border-color: #52b788;
    color: #d4f5dd; box-shadow: 0 0 10px rgba(82,183,136,.2);
  }

  /* Password strength */
  .strength-bar {
    height: 3px; background: rgba(255,255,255,.08); border-radius: 2px;
    overflow: hidden; margin-top: -8px;
  }
  .strength-fill { height: 100%; border-radius: 2px; transition: width .4s, background .4s; }
  .match-hint { font-size: .75rem; margin-top: 5px; display: block; }
  .match { color: #52b788; }
  .mismatch { color: #ff8888; }

  /* Error */
  .error-msg {
    background: rgba(220,60,60,.12); border: 1px solid rgba(220,60,60,.25);
    border-radius: 8px; padding: 10px 14px; font-size: .84rem; color: #ff9999;
    margin-top: .5rem;
  }

  /* Buttons */
  .btn-row {
    display: flex; gap: .75rem; margin-top: 1.4rem;
  }
  .btn-back {
    padding: 13px 18px;
    background: rgba(255,255,255,.06); border: 1px solid rgba(82,183,136,.2);
    border-radius: 11px; color: rgba(168,220,180,.7);
    font-size: .93rem; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background .2s;
  }
  .btn-back:hover { background: rgba(255,255,255,.1); }
  .btn-next {
    flex: 1; padding: 14px;
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
    border: none; border-radius: 11px; color: #fff;
    font-size: .95rem; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    box-shadow: 0 4px 18px rgba(82,183,136,.25);
    transition: transform .15s, box-shadow .2s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }
  .btn-next:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 26px rgba(82,183,136,.38); }
  .btn-next:disabled { opacity: .65; cursor: not-allowed; }
  .spinner {
    width: 15px; height: 15px; border: 2px solid rgba(255,255,255,.3);
    border-top-color: #fff; border-radius: 50%;
    animation: spin .7s linear infinite; display: inline-block;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .footer {
    text-align: center; margin-top: 1.4rem; font-size: .86rem;
    color: rgba(168,220,180,.4); display: flex; align-items: center;
    justify-content: center; gap: 6px;
  }
  .link-btn {
    background: none; border: none; color: #52b788; font-size: .86rem;
    font-weight: 600; font-family: 'DM Sans', sans-serif; cursor: pointer; padding: 0;
    transition: color .2s;
  }
  .link-btn:hover { color: #95d5b2; }
</style>
