from dataclasses import dataclass
from typing import List, Optional, Union

# 버튼 이름, 요청, url
@dataclass
class ButtonDTO:
    title: str
    payload: Optional[str] = None
    url: Optional[str] = None

# 사용자 인풋, 요청
@dataclass
class ChatRequestDTO:
    user_input: Optional[str] = None
    payload: str
    photo: Optional[str] = None

# 챗봇 응답, 버튼 목록
@dataclass
class ChatResponseDTO:
    message: str
    buttons: List[ButtonDTO]