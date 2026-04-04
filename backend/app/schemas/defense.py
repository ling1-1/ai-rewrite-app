from pydantic import BaseModel


class DefenseGenerationOptions(BaseModel):
    ppt_page_count: int = 5
    ppt_outline: str = (
        "一、研究背景、目的与意义\n"
        "二、研究内容重点介绍\n"
        "三、研究成果\n"
        "四、个人观点\n"
        "五、致谢"
    )
    speech_duration_minutes: int = 4
    language_style: str = "更直白"
    persona_style: str = "普通本科生"
    content_density: str = "精简"
    include_acknowledgement: bool = True
    include_personal_view: bool = True


class DefensePptRequest(DefenseGenerationOptions):
    thesis_text: str


class DefensePptResponse(BaseModel):
    ppt_content: str


class DefenseSpeechRequest(DefenseGenerationOptions):
    thesis_text: str
    ppt_content: str


class DefenseSpeechResponse(BaseModel):
    speech_content: str


class DefenseFlowResponse(BaseModel):
    ppt_content: str
    speech_content: str
