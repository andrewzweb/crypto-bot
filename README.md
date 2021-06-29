# Crypto-bot

## Main goals

- [x] get data about the order book
- [x] update data via websocket
- [x] print best ask and bit every minute in console

# Run bot 


Check version
---

Before starting, you must make sure that on the local computer the same version of python as in the file **deploy/runtime.txt**

Check local version
```sh
python -V
```

Print in console requirement version

```sh
cat deploy/runtime.txt
```

Install requirements lib
---

```sh
pip install deploy/requirements.txt
```

Run bot
---

```sh
python bot/bot.py
```
