from dataclasses import dataclass, field
from typing import Optional

# 업로드 된 사진
@dataclass
class ImageUploadDTO:
    image_file: bytes

# 정책 정보 - 00구
@dataclass
class PolicyInfoDTO:
    district_name: str

# 사용자 input
@dataclass
class UserInputDTO:
    user_input: str
