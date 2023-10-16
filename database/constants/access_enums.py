from enum import Enum

class Access(str, Enum):
  CREATOR = 'Creator'
  EDITOR = 'Editor'
  VIEWER = 'Viewer'