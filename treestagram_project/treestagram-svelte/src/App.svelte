<script>
  import { onMount } from "svelte";
  import { user, apiMe, initCSRF } from "./lib/api.js";
  import Login from "./routes/Login.svelte";
  import Signup from "./routes/Signup.svelte";
  import Home from "./routes/Home.svelte";
  import Landing from "./routes/Landing.svelte";
  import TreeDashboard from "./routes/TreeDashboard.svelte";
  import Chat from "./routes/Chat.svelte";
  import Profile from "./routes/Profile.svelte";

  let route = window.location.pathname;
  let ready = false;

  // Simple router
  function navigate(path) {
    window.history.pushState({}, "", path);
    route = path;
  }

  window.addEventListener("popstate", () => {
    route = window.location.pathname;
  });
  window.navigate = navigate; // global helper

  onMount(async () => {
    await initCSRF();
    const me = await apiMe();
    if (me && me.username) user.set(me);
    ready = true;
  });

  $: if (ready) {
    // Authenticated user visiting landing/login/signup → redirect to feed
    if ($user && (route === "/" || route === "/login" || route === "/signup")) {
      if (route !== "/home") navigate("/home");
    }
    // Unauthenticated user visiting protected pages → redirect to landing
    else if (
      !$user &&
      ["/home", "/dashboard", "/chat", "/profile"].includes(route)
    ) {
      navigate("/");
    }
  }
</script>

{#if ready}
  {#if route === "/signup"}
    <Signup {navigate} />
  {:else if route === "/login"}
    <Login {navigate} />
  {:else if route === "/home"}
    <Home {navigate} />
  {:else if route === "/dashboard"}
    <TreeDashboard {navigate} />
  {:else if route === "/chat"}
    <Chat {navigate} />
  {:else if route === "/profile"}
    <Profile {navigate} />
  {:else}
    <Landing {navigate} />
  {/if}
{:else}
  <!-- Splash loader -->
  <div class="splash">
    <div class="splash-tree">🌳</div>
    <div class="splash-ring"></div>
  </div>
{/if}

<style>
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  :global(html, body) {
    height: 100%;
    font-family: "DM Sans", sans-serif;
    background: #f5f0e8;
    color: #1a1108;
    overflow-x: hidden;
  }
  :global(body) {
    min-height: 100vh;
  }

  /* Scrollbar */
  :global(::-webkit-scrollbar) {
    width: 6px;
    height: 6px;
  }
  :global(::-webkit-scrollbar-track) {
    background: transparent;
  }
  :global(::-webkit-scrollbar-thumb) {
    background: #c5d5c5;
    border-radius: 3px;
  }

  .splash {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: #2c1810;
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
    border: 2px solid rgba(143, 188, 143, 0.4);
    animation: ripple 1.4s ease-out infinite;
  }
  @keyframes pulse {
    0%,
    100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.12);
    }
  }
  @keyframes ripple {
    0% {
      transform: scale(0.8);
      opacity: 1;
    }
    100% {
      transform: scale(2.2);
      opacity: 0;
    }
  }
</style>
