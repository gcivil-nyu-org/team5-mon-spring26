<script>
  import { page } from "$app/stores";

  $: treeId = $page.params.tree_id;
</script>

<h1>Tree Dashboard for {treeId}</h1>