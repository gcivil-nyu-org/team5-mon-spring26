<script>
  import { onMount } from 'svelte'
  import { user, apiMe, initCSRF } from './lib/api.js'
  import Login from './routes/Login.svelte'
  import Signup from './routes/Signup.svelte'
  import Home from './routes/Home.svelte'

  let route = window.location.pathname
  let ready = false

  // Simple router
  function navigate(path) {
    window.history.pushState({}, '', path)
    route = path
  }

  window.addEventListener('popstate', () => { route = window.location.pathname })
  window.navigate = navigate  // global helper

  onMount(async () => {
    await initCSRF()
    const me = await apiMe()
    if (me && me.username) user.set(me)
    ready = true
  })

  $: if (ready) {
    if ($user && (route === '/login' || route === '/signup' || route === '/')) {
      if (route !== '/home') navigate('/home')
    } else if (!$user && route === '/home') {
      navigate('/login')
    }
  }
</script>

{#if ready}
  {#if route === '/signup'}
    <Signup {navigate} />
  {:else if route === '/home'}
    <Home {navigate} />
  {:else}
    <Login {navigate} />
  {/if}
{:else}
  <!-- Splash loader -->
  <div class="splash">
    <div class="splash-tree">🌳</div>
    <div class="splash-ring"></div>
  </div>
{/if}

<style>
  :global(*) { box-sizing: border-box; margin: 0; padding: 0; }
  :global(html, body) {
    height: 100%;
    font-family: 'DM Sans', sans-serif;
    background: #0d1f14;
    color: #e8f5e4;
    overflow-x: hidden;
  }
  :global(body) { min-height: 100vh; }

  .splash {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
  .splash-tree {
    font-size: 3.5rem;
    animation: pulse 1.4s ease-in-out infinite;
    z-index: 2;
  }
  .splash-ring {
    position: absolute;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 2px solid rgba(82, 183, 136, 0.4);
    animation: ripple 1.4s ease-out infinite;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
  }
  @keyframes ripple {
    0%   { transform: scale(0.8); opacity: 1; }
    100% { transform: scale(2.2); opacity: 0; }
  }
</style>
