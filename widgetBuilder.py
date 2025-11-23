from openai import OpenAI
from data.keys import openaiKey

# be sure you have keys.py in data/ with your OpenAI key defined as openaiKey variable
client = OpenAI(
    api_key=openaiKey
)

systemMessage = '''

'''

messages = [
    {"role": "system", "content": systemMessage}
]

def getWidgetCode(prompt):

    messages.append({"role": "user", "content": prompt})
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = completion.choices[0].message.content
    messages.append({"role": "agent", "content": reply})
    
    return reply