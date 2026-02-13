from django.db import models

class College(models.Model):
    college_id = models.CharField(max_length=10, unique=True)
    college_name = models.CharField(max_length=100)

    def __str__(self):
        return self.college_name


class Department(models.Model):
    dept_id = models.CharField(max_length=10, unique=True)
    dept_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dept_name


class Semester(models.Model):
    sem_id = models.CharField(max_length=10, unique=True)
    sem_name = models.CharField(max_length=50)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.sem_name} ({self.year})"


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    credits = models.IntegerField(default=3)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject_name} ({self.semester.sem_name})"


class Student(models.Model):
    student_id = models.CharField(max_length=15, unique=True)
    student_name = models.CharField(max_length=50)
    student_age = models.PositiveIntegerField()
    joining_year = models.PositiveSmallIntegerField(blank=True, null=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='student_profiles/',blank=True,null=True)

    def __str__(self):
        return self.student_name

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField(null=True, blank=True)
    earned_credits = models.IntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.student} - {self.subject}"
