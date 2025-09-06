# -*- coding: utf-8 -*-

from burp import IBurpExtender, ITab, IContextMenuFactory
from javax.swing import (JPanel, JLabel, JTextField, JButton, JTextArea, JScrollPane, JComboBox,
                         BoxLayout, JOptionPane)
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection
from java.lang import Runnable
from java.lang import String
from java.util import ArrayList
from javax.crypto import Cipher
from javax.crypto.spec import SecretKeySpec, IvParameterSpec
from java.security import MessageDigest
from java.util import Base64

def to_hex(b):
    sb = []
    for x in b:
        sb.append('%02x' % (x & 0xff))
    return ''.join(sb)

def from_hex(s):
    s = s.replace(' ', '')
    if len(s) % 2 != 0:
        raise ValueError('Invalid hex string')
    out = bytearray()
    for i in range(0, len(s), 2):
        out.append(int(s[i:i+2], 16))
    return bytes(out)

class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("AES Helper")

        # AES Helper Tab
        self.aes_panel = JPanel()
        self.aes_panel.setLayout(BoxLayout(self.aes_panel, BoxLayout.Y_AXIS))

        # Key / IV
        keyPanel = JPanel()
        keyPanel.setLayout(BoxLayout(keyPanel, BoxLayout.X_AXIS))
        keyPanel.add(JLabel('Key: '))
        self.keyField = JTextField(48)
        keyPanel.add(self.keyField)
        keyPanel.add(JLabel('  IV: '))
        self.ivField = JTextField(32)
        keyPanel.add(self.ivField)
        self.aes_panel.add(keyPanel)

        # Mode / Padding / Input / Output / Key Size
        cfgPanel = JPanel()
        cfgPanel.setLayout(BoxLayout(cfgPanel, BoxLayout.X_AXIS))
        cfgPanel.add(JLabel('Mode: '))
        self.modeBox = JComboBox(['CBC','ECB','CFB','OFB','CTR'])
        cfgPanel.add(self.modeBox)
        cfgPanel.add(JLabel('  Padding: '))
        self.padBox = JComboBox(['PKCS5Padding','NoPadding','ZeroPadding'])
        cfgPanel.add(self.padBox)
        cfgPanel.add(JLabel('  Input type: '))
        self.inBox = JComboBox(['Plain Text','Hex','Base64'])
        cfgPanel.add(self.inBox)
        cfgPanel.add(JLabel('  Output type: '))
        self.outBox = JComboBox(['Plain Text','Hex','Base64'])
        cfgPanel.add(self.outBox)
        cfgPanel.add(JLabel('  Key Size (bits): '))
        self.keySizeBox = JComboBox(['128','192','256'])
        cfgPanel.add(self.keySizeBox)
        self.aes_panel.add(cfgPanel)

        # Input / Output areas
        self.inputArea = JTextArea(8,80)
        self.outputArea = JTextArea(8,80)
        self.aes_panel.add(JLabel('Input:'))
        self.aes_panel.add(JScrollPane(self.inputArea))
        btnPanel = JPanel()
        btnPanel.setLayout(BoxLayout(btnPanel, BoxLayout.X_AXIS))
        encryptBtn = JButton('Encrypt', actionPerformed=self.encrypt)
        decryptBtn = JButton('Decrypt', actionPerformed=self.decrypt)
        clearBtn = JButton('Clear', actionPerformed=self.clear)
        copyBtn = JButton('Copy output', actionPerformed=self.copy_output)
        btnPanel.add(encryptBtn)
        btnPanel.add(decryptBtn)
        btnPanel.add(clearBtn)
        btnPanel.add(copyBtn)
        self.aes_panel.add(btnPanel)
        self.aes_panel.add(JLabel('Output:'))
        self.aes_panel.add(JScrollPane(self.outputArea))

        callbacks.addSuiteTab(self)
        callbacks.registerContextMenuFactory(self)
        self._callbacks.printOutput('AES Helper loaded.')

    # ITab interface
    def getTabCaption(self):
        return "AES Helper"

    def getUiComponent(self):
        return self.aes_panel

    # AES functions
    def clear(self, event=None):
        self.inputArea.setText('')
        self.outputArea.setText('')

    def copy_output(self, event=None):
        text = self.outputArea.getText()
        if text:
            Toolkit.getDefaultToolkit().getSystemClipboard().setContents(StringSelection(text), None)
            JOptionPane.showMessageDialog(None, 'Output copied to clipboard')

    def encrypt(self, event=None):
        self._aes_operation_wrapper('encrypt')

    def decrypt(self, event=None):
        self._aes_operation_wrapper('decrypt')

    def _aes_operation_wrapper(self, op):
        try:
            key_b, iv_b = self._get_key_iv()
            mode = str(self.modeBox.getSelectedItem())
            padding = str(self.padBox.getSelectedItem())
            input_type = str(self.inBox.getSelectedItem())
            output_type = str(self.outBox.getSelectedItem())
            key_size = int(str(self.keySizeBox.getSelectedItem()))
            data_text = self.inputArea.getText() or ''

            # Convert input according to input type
            if input_type=='Hex':
                data_bytes = from_hex(data_text)
            elif input_type=='Base64':
                data_bytes = Base64.getDecoder().decode(data_text)
            else:
                data_bytes = data_text.encode('utf-8')

            # Adjust key size
            if len(key_b)*8 != key_size:
                h = MessageDigest.getInstance('SHA-256')
                key_b = h.digest(key_b)[:key_size//8]

            transformation = 'AES/%s/%s' % (mode, padding if padding!='ZeroPadding' else 'NoPadding')
            cipher = Cipher.getInstance(transformation)
            skey = SecretKeySpec(key_b,'AES')
            ivspec = None
            if mode != 'ECB':
                if iv_b is None or len(iv_b)==0:
                    iv_b = bytearray([0]*16)
                if len(iv_b)<16:
                    iv_b = iv_b + bytearray([0]*(16-len(iv_b)))
                ivspec = IvParameterSpec(iv_b[:16])

            if op=='encrypt':
                if ivspec is None:
                    cipher.init(Cipher.ENCRYPT_MODE, skey)
                else:
                    cipher.init(Cipher.ENCRYPT_MODE, skey, ivspec)
                if padding=='ZeroPadding':
                    bs = 16
                    pad_len = (bs - (len(data_bytes)%bs))%bs
                    data_bytes = data_bytes + bytearray([0]*pad_len)
                result = cipher.doFinal(data_bytes)
            else:
                if ivspec is None:
                    cipher.init(Cipher.DECRYPT_MODE, skey)
                else:
                    cipher.init(Cipher.DECRYPT_MODE, skey, ivspec)
                result = cipher.doFinal(data_bytes)

            # Convert to output type
            if output_type=='Hex':
                out = to_hex(result)
            elif output_type=='Base64':
                out = Base64.getEncoder().encodeToString(result)
            else:
                try:
                    out = String(result,'UTF-8')
                except Exception:
                    out = Base64.getEncoder().encodeToString(result)

            self.outputArea.setText(out)

        except Exception as e:
            JOptionPane.showMessageDialog(None,'AES Error: %s' % str(e))

    def _get_key_iv(self):
        key_text = self.keyField.getText() or ''
        iv_text = self.ivField.getText() or ''
        try:
            if all(c in '0123456789abcdefABCDEF ' for c in key_text) and len(key_text.replace(' ','')) in (32,48,64):
                key_b = from_hex(key_text)
            else:
                key_b = key_text.encode('utf-8')
        except Exception:
            key_b = key_text.encode('utf-8')

        try:
            if all(c in '0123456789abcdefABCDEF ' for c in iv_text) and len(iv_text.replace(' ',''))==32:
                iv_b = from_hex(iv_text)
            else:
                iv_b = iv_text.encode('utf-8') if iv_text else None
        except Exception:
            iv_b = iv_text.encode('utf-8') if iv_text else None
        return key_b, iv_b

    # Context menu
    def createMenuItems(self, invocation):
        menu_list = ArrayList()
        selected = invocation.getSelectedMessages()
        if selected is None or len(selected)==0:
            return menu_list
        from javax.swing import JMenuItem
        item = JMenuItem('AES Helper: Load selection into AES Helper',
                         actionPerformed=lambda ev, inv=invocation: self._load_selection(inv))
        menu_list.add(item)
        return menu_list

    def _load_selection(self, invocation):
        try:
            msgs = invocation.getSelectedMessages()
            if msgs is None or len(msgs)==0:
                JOptionPane.showMessageDialog(None,'No message selected')
                return
            msg = msgs[0]
            bounds = invocation.getSelectionBounds()
            if bounds is None:
                JOptionPane.showMessageDialog(None,'No selection area')
                return
            start,end = bounds[0], bounds[1]
            raw = msg.getRequest() if msg.getRequest() is not None else msg.getResponse()
            if raw is None:
                JOptionPane.showMessageDialog(None,'No request/response data')
                return
            raw_bytes = bytearray(raw)
            sel_bytes = raw_bytes[start:end]
            try:
                sel_text = sel_bytes.decode('utf-8')
            except Exception:
                sel_text = Base64.getEncoder().encodeToString(sel_bytes)
            def set_text():
                self.inputArea.setText(sel_text)
                JOptionPane.showMessageDialog(None,'Selection loaded into AES Helper input area')
            self._callbacks.invokeLater(Runnable(set_text))
        except Exception as e:
            JOptionPane.showMessageDialog(None,'Error loading selection: %s' % str(e))
