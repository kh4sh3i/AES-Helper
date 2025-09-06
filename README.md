<h1 align="center">
  <a><img src="/img/logo.svg" alt="" width="200px"></a>
  <br>
  <img src="https://img.shields.io/badge/PRs-welcome-blue">
  <img src="https://img.shields.io/github/last-commit/kh4sh3i/AES-Helper">
  <img src="https://img.shields.io/github/commit-activity/m/kh4sh3i/AES-Helper">
  <a href="https://twitter.com/intent/follow?screen_name=kh4sh3i_"><img src="https://img.shields.io/twitter/follow/kh4sh3i_?style=flat&logo=twitter"></a>
  <a href="https://github.com/kh4sh3i"><img src="https://img.shields.io/github/stars/kh4sh3i?style=flat&logo=github"></a>
</h1>


# AES Helper
This repository contains a **Burp Suite extension (Jython)** that provides AES encryption and decryption utilities. It is designed to help penetration testers and security researchers work with AES-encrypted payloads directly inside Burp.

---

## Features
- Adds a custom Burp tab (**AES Helper**) with:
  - Input fields for AES Key and IV (hex or plain text)
  - Mode selection (CBC / ECB)
  - Text input/output areas
  - Encrypt / Decrypt / Swap buttons
- Right-click context menu options on requests/responses to:
  - Encrypt request body
  - Decrypt response body
- AES implementation using Java Crypto (`AES/CBC/PKCS5Padding` or `AES/ECB/PKCS5Padding`)
- Keys can be entered as **hex** or **plain text**
- Output encoded in **Base64**

---

## Installation
1. Download and install **Jython standalone** (e.g. `jython-standalone-2.7.x.jar`).
2. In Burp Suite, go to:
   - **Extender → Options → Python Environment** → set the path to the Jython jar.
3. In **Extender → Extensions → Add**, select:
   - Extension type: **Python**
   - Extension file: `burp_aes_extension.py`

Once loaded, you should see a new tab in Burp called **AES Helper**.

---

## Usage
### In AES Helper Tab
1. Enter a valid AES key (16/24/32 bytes). You can input it as hex (`00112233445566778899AABBCCDDEEFF`) or as plain text (`mysecretkey123456`).
2. If using CBC mode, enter a 16-byte IV (hex or plain text).
3. Paste plaintext or Base64-encoded ciphertext into the input area.
4. Click **Encrypt** or **Decrypt**.
5. Use **Swap In/Out** to move output back to input.

### In Context Menu
1. Right-click on a request/response inside Burp.
2. Select **AES Encrypt selection** (for request bodies) or **AES Decrypt selection** (for response bodies).
3. The body will be replaced with the encrypted/decrypted result.

---

## Requirements
- Burp Suite (Community or Pro)
- Jython Standalone (2.7+)


---

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