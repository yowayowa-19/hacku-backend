from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Akubi(BaseModel):
    user_id: int
    yawned_at: Optional[datetime] = None  # サーバーで生成するから不要
    latitude: float
    longitude: float


class AkubiResult(BaseModel):
    last_yawned_at: datetime


class LastAkubi(BaseModel):
    user_id: int
    last_yawned_at: datetime


class AkubiCombo(BaseModel):
    user_id: int
    combo_count: int
    distance: float
    akubis: list[Akubi]
    last_yawned_at: datetime


class UserCredential(BaseModel):
    name: str
    password: str


class UserId(BaseModel):
    id: int


class Ranking(BaseModel):
    contain_user_id: bool
    first_id: int
    end_id: int
    total_combo_count: int
    total_distance: float
    rank: int


class TotalRanking(BaseModel):
    combo_ranking: list[Ranking]
    distance_ranking: list[Ranking]
