from enum import Enum


class MessageRole(str, Enum):
    system = 'system',
    user = 'user',
    ai = 'ai',
    mentor = 'mentor',
    function = 'function',
    summary = 'summary'
