from django.http import QueryDict
from pydantic import (
    BaseModel,
    Field,
)


class GetPreSignedURLRequest(BaseModel):
    file_name: str = Field(description='Defined file name')

    @classmethod
    def of(cls, request: QueryDict):
        return cls(
            file_name=request.get('file_name'),
        )
