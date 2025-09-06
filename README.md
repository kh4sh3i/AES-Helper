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

## Limitations
- Only **Base64** ciphertext supported in the helper tab.
- Context-menu encryption/decryption replaces the **entire body** (not just selected parts). Manual adaptation may be needed for some formats (e.g. JSON, URL-encoded, chunked data).
- AES modes supported: **CBC** and **ECB** only.
- Ensure you update `Content-Length` headers if needed after modifying requests.

---

## Example
**Encrypting:**
- Key: `00112233445566778899AABBCCDDEEFF`
- IV: `0102030405060708090A0B0C0D0E0F10`
- Mode: CBC
- Input: `HelloWorld`
- Output: `U2FsdGVkX1...` (Base64 ciphertext)

**Decrypting:**
- Input: `U2FsdGVkX1...`
- Output: `HelloWorld`

---

## Author
Developed by [kh4sh3i].

---

## Roadmap / Ideas
- Add support for hex/plaintext output (not just Base64)
- Add support for GCM mode
- Context menu for selected text only (instead of whole body)
- Option to auto-fix `Content-Length` headers

