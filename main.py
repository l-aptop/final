from bleach.sanitizer import Cleaner
from bleach.linkifier import Linker
from sanic import Sanic
from colorama import init, Fore
from sanic.response import file
from time import time
from asyncio.futures import CancelledError
connected = []
cleaner = Cleaner(tags=[])
app = Sanic('chat')
bot = 'Chat Bot'
run_ip = "127.46.6.4"
port = 8080
init()


def open_in_new_tab(attrs, *args):
    attrs[(None, 'target')] = '_blank'
    return attrs


linker = Linker(callbacks=[open_in_new_tab])


def clean(text):
    return cleaner.clean(text)


def transform(text):
    return linker.linkify(clean(text.strip()))


def lstrip(text):
    return text.lower().strip()


async def broadcast(content):
    for user in connected:
        await user.send(content)


@app.route('/')
async def main(request):
    return await file('index.html')


@app.route('/script.js')
async def script(request):
    return await file('script.js')


@app.route('/style.css')
async def style(request):
    return await file('style.css')


@app.websocket('/socket')
async def chat(request, ws):
    username = request.args.get('username', 'None').strip()
    username_l = username.lower()
    if username_l in ('system', bot.lower()) or username_l == "" or len(username) > 12:
        print(Fore.YELLOW + '[INFO] Failed connection attempt: Username not allowed (username: {})'.format(username)
              + Fore.RESET)
        return await ws.send('{"error": "Username not allowed.", "code": 0}')
    for user in connected:
        if lstrip(user.username) == username_l:
            print(Fore.YELLOW + "[INFO] Failed connection attempt: Username already connected (username: {})"
                  .format(username) + Fore.RESET)
            return await ws.send('{"error": "Someone with that username is already connected.", "code": 0}')
    username = clean(username).replace('\\', '\\\\')
    ws.username = username
    ws.last = time()
    connected.append(ws)
    await ws.send(
        '{"username": "System", "message": "Connected to chat successfully!<br>'
        'There are AMOUNT people online.<br><br>'
        'To view available Chat Bot commands, say !help"}'.replace('AMOUNT', str(len(connected)), 1)
    )
    print(Fore.GREEN + '[INFO] {} connected'.format(username) + Fore.RESET)
    await broadcast('{"username": "System", "message": "<b>' + username + '</b> has joined the chat."}')
    try:
        async for msg in ws:
            msg = transform(msg).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '<br>')
            if msg != "" and len(msg) < 500 and (time() - ws.last) > 0.500:
                ws.last = time()
                print('{}: {}'.format(username, msg))
                if msg.startswith('!'):
                    if msg == '!help':
                        await ws.send('{"username": "' + username + '", "message": "' + msg + '"}')
                        await ws.send('{"username": "' + bot + '", "message": "<br>Hi <b>' + username +
                                      '</b>! My commands:<br>!online - shows everyone currently online"}')
                    elif msg == "!online":
                        await ws.send('{"username": "' + username + '", "message": "' + msg + '"}')
                        online = ""
                        for user in connected:
                            online += user.username + '<br>'
                        await ws.send('{"username": "' + bot + '", "message": "<br>Online people:<br>' + online + '"}')
                    else:
                        await ws.send('{"username": "' + username + '", "message": "' + msg + '"}')
                        await ws.send(
                            '{"username": "' + bot + '", "message": '
                            '"<br>Command not found! You can view my commands by using !help '
                            '(and also, all messages with a ! at the start are commands)"}'
                        )
                else:
                    await broadcast('{"username": "' + username + '", "message": "' + msg + '"}')
    except Exception as e:
        if isinstance(e, CancelledError) is not True:
            print(Fore.RED + '[ERROR] {}: {}'.format(type(e).__name__, str(e)) + Fore.RESET)
    finally:
        connected.remove(ws)
        print(Fore.YELLOW + '[INFO] {} disconnected'.format(username) + Fore.RESET)
        return await broadcast('{"username": "System", "message": "<b>' + username + '</b> has left the chat."}')

if __name__ == "__main__":
    app.run(host=run_ip, port=port, access_log=False)
