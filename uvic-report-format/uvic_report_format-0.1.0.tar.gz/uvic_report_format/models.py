from pydantic_yaml import YamlModel
from pydantic import EmailStr, FilePath
from typing import Literal
from pathlib import Path

Term = Literal["Spring", "Fall", "Summer"]


class StudentInfo(YamlModel):
    title: str
    year: int
    name: str
    student_id: str
    email: EmailStr
    employer: str
    location: str
    institution: str = "University of Victoria"
    faculty: str = "Engineering and Computer Science"
    term: Term = "Summer"


class Content(YamlModel):
    glossary: FilePath
    executive_summary: FilePath
    personal_reflection: FilePath
    introduction: FilePath
    body: FilePath
    conclusion: FilePath
    references: FilePath


class Config(YamlModel):
    output: Path


class Report(YamlModel):
    info: StudentInfo
    content: Content
    config: Config



