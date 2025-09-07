<h1 align="center">
  <a><img src="/img/logo.svg" alt="" width="200px"></a>
  <br>
  <img src="https://img.shields.io/badge/PRs-welcome-blue">
  <img src="https://img.shields.io/github/last-commit/kh4sh3i/AES-Helper">
  <img src="https://img.shields.io/github/commit-activity/m/kh4sh3i/AES-Helper">
  <a href="https://twitter.com/intent/follow?screen_name=kh4sh3i_"><img src="https://img.shields.io/twitter/follow/kh4sh3i_?style=flat&logo=twitter"></a>
  <a href="https://github.com/kh4sh3i"><img src="https://img.shields.io/github/stars/kh4sh3i?style=flat&logo=github"></a>
</h1>


# 🔐 AES Helper – Burp Extension

A **Burp Suite Jython extension** to **encrypt/decrypt AES payloads** directly inside Burp.

---

## ✨ Features
- 🔑 AES Key & IV input (hex or text)  
- ⚙️ Modes: CBC / ECB  
- 📝 Encrypt / Decrypt / Swap buttons  
- 📜 Right-click: Encrypt request / Decrypt response  
- 📦 Output in Base64  

---

## 🚀 Install
1. Install **Jython (2.7+)**  
2. In Burp:  
   - `Extender → Options → Python Environment → Jython jar`  
   - `Extender → Extensions → Add → Python → burp_aes_extension.py`  
3. Tab **AES Helper** will appear ✅  

---

## 🖥️ Usage
- Enter AES Key (16/24/32 bytes) & IV (for CBC)  
- Paste plaintext/Base64 → **Encrypt/Decrypt**  
- Use **Swap** to move output back  
- Right-click requests/responses → AES Encrypt/Decrypt  



# Chrome DevTools console snippet
* TIPS : remove length 16, 24 for better result to find IV and AES Key in javascript file

```javascript
(function () {
  const seen = new Set(); // track unique strings
  const validLengths = new Set([16, 24, 32]);

  function scanScript(code, sourceName) {
    const lines = code.split(/\r?\n/);
    const regex = /"((?:\\.|[^"\\])*)"/g; // match only double-quoted strings

    lines.forEach((line, idx) => {
      for (const match of line.matchAll(regex)) {
        const raw = match[1];
        const value = raw
          .replace(/\\n/g, '\n')
          .replace(/\\r/g, '\r')
          .replace(/\\t/g, '\t')
          .replace(/\\"/g, '"')
          .replace(/\\\\/g, '\\');
        if (validLengths.has(value.length) && !seen.has(value)) {
          seen.add(value);
          console.log(`${sourceName}:${idx + 1}: "${value}" (length=${value.length})`);
        }
      }
    });
  }

  document.querySelectorAll("script").forEach((s, i) => {
    if (s.src) {
      // external script (blocked if CORS not allowed)
      fetch(s.src).then(r => r.text()).then(code => {
        scanScript(code, s.src);
      }).catch(() => {
        console.warn("Skipped (CORS blocked):", s.src);
      });
    } else if (s.textContent.trim()) {
      scanScript(s.textContent, `inline-script-${i+1}`);
    }
  });
})();
```