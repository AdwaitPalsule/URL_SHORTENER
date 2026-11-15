from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl

class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_alias : str |None =None                      # rejects "abc" or "ftp:/bad"
class UpdateLinkRequest(BaseModel):
    url :HttpUrl

class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # build from the ORM object
    short_code: str
    original_url: str
    created_at: datetime