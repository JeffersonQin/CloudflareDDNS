# CloudflareDDNS

## Description

DDNS tool for Cloudflare. A software with a GUI written by PyQt5. This software will automatically update your current DNS to the link you want to update.

## Author

Author: Haoyun Qin

## Usage

- X_AUTH_KEY: Global API Key.
- ZONE_ID: Can be checked on the web page.
- DNS_RECORD_NAME: The DNS_Record name for your website.
- WEBSITE_URL: URL for your website.

Exact Descriptions and official APIs: https://api.cloudflare.com/

## PyInstaller parameters

```shell
pyinstaller ddns.py -w --clean --hidden-import PyQt5.sip -F
```
