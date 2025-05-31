import datetime
from pydantic import BaseModel

class SessionBase(BaseModel):
  name: str
  start_date: datetime.date
  end_date: datetime.date



class SessionCreate(SessionBase):
  pass


class SessionSchema(SessionBase):
  id: int

  model_config = {'from_attributes': True}
