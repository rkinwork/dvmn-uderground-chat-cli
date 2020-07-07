# Devman underground chat Reader/Sender

Two useful scripts to read and send messages. It is working with socket connection.
This project created for study proposes. It is a part of [dvmn.org](https://dvmn.org/modules/async-python) async python course.

### Prerequisites

This script has been developed using  `python == 3.8`

Have installed:
* [git](https://git-scm.com/)
* [pyenv](https://github.com/pyenv/pyenv)
* [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

### Installing

Prepare execution environment
```bash
git clone git@github.com:rkinwork/dvmn-uderground-chat-cli.git
pyenv install 3.8.2
cd dvmn-uderground-chat-cli
pyenv virtualenv 3.8.2 dvmn-uderground-chat-cli
pyenv activate dvmn-uderground-chat-cli
```

Install dependencies

```bash
pip3 install -r requirements.txt
```

### How to listen underground chat
In first terminal 
```bash
python listen-minechat.py
```
Use `ctrl+c` to kill program

This script will add chat history to  `minechat.history` file
To view it in live mode execute this command in another terminal

```bash
tail -f minechat.history
```

To see all available settings

```bash
python listen-minechat.py -h
```

### How to send a message to chat

Send your first message with `token`, if you don't have token send it with 
your nickname and don't forget to save `token`

```bash
python send-minechat.py -n supernickname -m "my first message"
# Save your token: 21f9b692-c071-11ea-8c47-0242xxxxxxx
# Message has been sent successfully
``` 
```bash
python send-minechat.py -t 21f9b692-c071-11ea-8c47-0242ac110002 -m "my first message with token"
# Message has been sent successfully
```

To see all available settings

```bash
python send-minechat.py -h
```

For example, you can switch on debug mode or redefine connection setting.
All you can do via cli arguments, ENV variables or 
creating `conf.ini` file in the project root 


## Authors

* **Roman Kazakov** 
* **DVMN.ORG team**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

