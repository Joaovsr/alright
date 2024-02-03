# [alright](#)
This is a Fork of [**alright**](https://github.com/Kalebu/alright)

## Getting started

You need to do a little bit of work to get [**alright**](https://github.com/Kalebu/alright) running, but don't worry I got you, everything will work well if you just carefully follow through the documentation.

### Installation

You first need to clone or download the repo to your local directory and then move into the project directory as shown in the example and then run the command below;

```bash
git clone gh repo clone Joaovsr/alright
cd alright
alright > python setup.py install 
....
```

### Setting up Selenium

Underneath alright is **Selenium** which is what does all the automation work by directly controlling the browser, so you need to have a selenium driver on your machine for **alright** to work. But luckily alright uses [webdriver-manager](https://pypi.org/project/webdriver-manager/), which does this automatically. You just need to install a browser. By default alright uses [Google Chrome](https://www.google.com/chrome/).

## What you can do with alright?

- [Send Messages](#sending-messages)
- [Send Images](#sending-images)
- [Send Videos](#sending-videos)
- [Send Documents](#sending-documents)
- [Get first chat](#get-first-chat)
- [Search chat by name](#search-chat-by-name)
- [logout](#logout)

*When you're running your program made with **alright**, you can only have one controlled browser window at a time. Running a new window while another window is live will raise an error. So make sure to close the controlled window before running another one*

### Unsaved contact vs saved contacts

Alright allows you to send the messages and media to both saved and unsaved contacts as explained earlier. But there is a tiny distinction on how you do that, you will observe this clearly as you use the package.

The first step before sending anything to the user is first to locate the user and then you can start sending the information, thats where the main difference lies between saved and unsaved contacts.

#### Saved contacts

To saved contact use method *find_by_username()* to locate a saved user. You can also use the same method to locate WhatsApp groups. The parameter can either be;

- saved username
- mobile number
- group name

Here an Example on how to do that

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_by_username('saved-name or number or group')
```

#### Unsaved contacts

In sending message to unsaved whatsapp contacts use *find_user()* method to locate the user and the parameter can only be users number with country code with (+) omitted as shown below;

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_user('255-74848xxxx')
```

Now Let's dive in on how we can get started on sending messages and medias

### Sending Messages

>Use this if you don't have WhatsApp desktop installed

To send a message with alright, you first need to target a specific user by using *find_user()* method (include the **country code** in your number without the '+' symbol) and then after that you can start sending messages to the target user using *send_message()* method as shown in the example below;

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_user('2557xxxxxz')
>>> messages = ['Morning my love', 'I wish you a good night!']
>>> for message in messages:  
        messenger.send_message(message)    
```
#### Multiple numbers

Here how to send a message to multiple users, Let's say we want to wish merry-x mass to all our contacts, our code is going to look like this;

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> numbers = ['2557xxxxxx', '2557xxxxxx', '....']
>>> for number in numbers:
        messenger.find_user(number)
        messenger.send_message("I wish you a Merry X-mass and Happy new year ")
```

*You have to include the **country code** in your number for this library to work but don't include the (+) symbol*


> If you're sending media either picture, file, or video each of them have an optional parameter called <message> which is usually the caption to accompany the media. 

### Sending Images

Sending Images is nothing new, its just the fact you have to include a path to your image and the message to accompany the image instead of just the raw string characters and also you have use *send_picture()*, Here an example;


```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_user('mobile')
>>> messenger.send_picture('path-to-image-without-caption')
>>> messenger.send_picture('path-to-image',"Text to accompany image")
```

### Sending Videos

Similarly, to send videos just use the *send_video()*  method;

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_user('mobile')
>>> messenger.send_video('path-to-video')
```

>

### Sending Documents

To send documents such as docx, pdf, audio etc, you can use the *send_file()* method to do that;

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.find_user('mobile')
>>> messenger.send_file('path-to-file')
```

### Check if a chat has unread messages or not

This method checks if a chat, which name is passed as a *query* parameter, has got unread messages or not.

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.check_if_given_chat_has_unread_messages(query="Chat 123")
```
        
### Get first chat

This method fetches the first chat in the list on the left of the web app - since they are not ordered in an expected way, a fair workaround is applied. One can also ignore (or not ignore) pinned chats (placed at the top of the list) by passing the parameter *ignore_pinned* to do that - default value is `ignore_pinned=True`.

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.get_first_chat()
```

### Search chat by name

This method searches the opened chats by a partial name provided as a `query` parameter, returning the first match. Case sensitivity is treated and does not impact the search.

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.search_chat_by_name(query="Friend")
```
        
### Get last message received in a given chat

This method searches for the last message received in a given chat, received as a `query` parameter, returning the sender, text and time. Groups, numbers and contacts cases are treated, as well as possible non-received messages, video/images/stickers and others.

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.get_last_message_received(query="Friend")
```
        
### Retrieve all chat names with unread messages

This method searches for all chats with unread messages, possibly receiving parameters to `limit` the search to a `top` number of chats or not, returning a list of chat names.

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.fetch_all_unread_chats(limit=True, top=30)
```

#### DISCLAIMER: Apparently, `fetch_all_unread_chats` functionallity works on most updated browser versions (for example, `Chrome Version 102.0.5005.115 (Official Build) (x86_64)`). If it fails with you, please consider updating your browser while we work on an alternatives for non-updated broswers.
        
### logout from whatsapp

You can sign out of an account that is currently saved

```python
>>> from alright import WhatsApp
>>> messenger = WhatsApp()
>>> messenger.logout()
```
