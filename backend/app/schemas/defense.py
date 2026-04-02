from pydantic import BaseModel


class DefensePptRequest(BaseModel):
    thesis_text: str


class DefensePptResponse(BaseModel):
    ppt_content: str


class DefenseSpeechRequest(BaseModel):
    thesis_text: str
    ppt_content: str


class DefenseSpeechResponse(BaseModel):
    speech_content: str


class DefenseFlowResponse(BaseModel):
    ppt_content: str
    speech_content: str
