<div align="center">
  <a href="https://github.com/EndstoneMC/endstone/releases">
    <img src="https://minecraft.wiki/images/Warped_Hyphae_%28UD%29_JE1_BE1.gif" width="160" height="160">
  </a>

  <h2>Warps</h2>
  <p><b>A lightweight warp plugin for Endstone.</b></p>
</div>

<p align="center">
  <a href="https://github.com/Rezn1r/endstone-warps/actions/workflows/lint.yml">
    <img src="https://github.com/Rezn1r/endstone-warps/actions/workflows/lint.yml/badge.svg">
  </a>
  <a href="https://github.com/Rezn1r/endstone-warps/actions/workflows/build.yml">
    <img src="https://github.com/Rezn1r/endstone-warps/actions/workflows/build.yml/badge.svg">
  </a>
  <a href="https://github.com/Rezn1r/endstone-warps/actions/workflows/release.yml">
    <img src="https://github.com/Rezn1r/endstone-warps/actions/workflows/release.yml/badge.svg">
  </a>
</p>
</div>

<h3>Installation</h3>
<hr>
<p>Download the latest release from the <a href="https://github.com/Rezn1r/endstone-warps/releases">GitHub releases</a> page. or install via pip:</p>
<pre><code>pip install endstone-warps
</code></pre>

<h3>Configuration</h3>
<hr>
<p>Warps can be configured in the <code>config.toml</code> file.</p>

```toml
[database]
# Database configuration
type = "sqlite"
name = "warps.db"

[warp]
# Countdown duration in seconds before teleporting
countdown_duration = 3
# Cooldown between warps in seconds
cooldown_seconds = 5
```

<h3>Commands</h3>
<hr>
<ul>
  <li><code>/warp [name]</code> - Teleport to a warp point.</li>
  <li><code>/setwarp [name]</code> - Set a warp point at your current location.</li>
  <li><code>/delwarp [name]</code> - Delete a warp point.</li>
  <li><code>/warps</code> - List all available warp points.</li>
</ul>

<h3>Building from Source</h3>
<hr>
<p>Clone the repository and build using `uv`:</p>
<pre><code>git clone https://github.com/Rezn1r/endstone-warps.git
cd endstone-warps
uv run build --wheel
</code></pre>
<p>The built wheel file will be located in the <code>dist/</code> directory.</p>