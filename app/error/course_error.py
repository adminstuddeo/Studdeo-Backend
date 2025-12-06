class CourseNotFound(Exception):
    def __init__(self, message: str = "Course not found") -> None:
        super().__init__(message)
