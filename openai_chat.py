MESSAGE_HISTORY_LENGTH = 6
SYSTEM_MESSAGE = "You are an AI assistant named Stevey being accessed by multiple users via Discord. Human users will have their messages prefixed by their usernames. Stevey should NOT prefix your messages with 'Stevey:' and should instead just contain the message."
class Chat:

    def __init__(self, openai_client, channel_id):
        self.message_history = []
        self.users = []
        self.client = openai_client
        self.channel_id = channel_id

    def send_message(self, user, message, image_url):
        if image_url:
            model="gpt-4-vision-preview"
            self.message_history.append(ImageChatMessage('user', user, message, image_url))
        else:
            model="gpt-3.5-turbo"
            self.message_history.append(ChatMessage('user', user, message))

        messages = list(map(lambda m: m.getJSON(), self.message_history[-MESSAGE_HISTORY_LENGTH:]))
        messages.insert(0, ChatMessage('system', 'system', SYSTEM_MESSAGE).getJSON())

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=256,
        )
        print("[RESPONSE DEBUG INFO]")
        print("Model used: " + response.model)
        print("Finish reason: " + response.choices[0].finish_reason)

        self.message_history.append(ChatMessage('assistant', 'Stevey', response.choices[0].message.content))
        return response.choices[0].message.content

class ChatMessage:
    def __init__(self, role, user, content):
        self.role = role
        self.user = user
        msg = user +": " + content if role == "user" else content
        self.content = [{"type": "text", "text": msg}]

    def getJSON(self):
        return {
            "role": self.role,
            "content": self.content
        }
    
class BotMessage(ChatMessage):
    def __init__(self, content):
        super().__init__("assistant", "Stevey", content)

class ImageChatMessage(ChatMessage):
    def __init__(self, role, user, content, image_url):
        super().__init__(role, user, content)
        self.content.append({"type":"image_url", "image_url": image_url})
