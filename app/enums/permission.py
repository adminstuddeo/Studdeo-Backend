from enum import StrEnum, auto


class Permission(StrEnum):
    CREATE_USER = auto()
    UPDATE_USER = auto()
    DELETE_USER = auto()
    READ_EXTERNAL_USERS = auto()
    READ_ALL_COURSES = auto()
    READ_COURSES = auto()
    READ_LESSONS = auto()
    READ_SALES = auto()
    READ_STUDENTS = auto()
    READ_USERS = auto()
