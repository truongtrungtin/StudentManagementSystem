from django.db.models.aggregates import Count

from API.models import (CustomUser, Staffs, Students, ImageStudent,
                        Trainers, Classes, Courses, Lessons, ClassCourse,
                        StatusAttendance, Attendance, Faculties, ClassRoom, Slots)
import random as rnd
from datetime import datetime, timedelta, date

POPULATION_SIZE = 4
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.1


class Schedule:
    def __init__(self):
        self._Attendance = []
        self._Classcourse = []
        self._fitnessAttendance = -1
        self._fitnessClasscourse = -1
        self._isFitnessChanged = True
        self._numbOfConflictsAttendance = 0
        self._numbOfConflictsClasscourse = 0

    def get_Attendance(self):
        return self._Attendance

    def get_Classcourse(self):
        return self._Classcourse

    def get_numbOfConflictsAttendance(
        self): return self._numbOfConflictsAttendance

    def get_numbOfConflictsClasscourse(
        self): return self._numbOfConflictsClasscourse

    def get_fitness(self):
        if(self._isFitnessChanged == True):
            self._fitnessAttendance = self.calculate()[0]
            self._fitnessClasscourse = self.calculate()[1]
            self._isFitnessChanged = False
        return (self._fitnessAttendance + self._fitnessClasscourse) / 2

    def initialize(self, data):
        classcourse = ClassCourse.objects.filter(Class__faculty__id=data[0].user.faculty.id, Class_id=data[1]).annotate(attendances = Count('attendance')).filter(attendance__ClassRoom=None)
        if data[3] != None:
            classcourse = ClassCourse.objects.filter(Class_id=data[1], Course_id=data[4]).annotate(attendances=Count('attendance')).filter(attendance__ClassRoom=None)
        trainer = Trainers.objects.filter(
            admin__faculty__id=data[0].user.faculty.id)
        slots = Slots.objects.all()
        classrooms = ClassRoom.objects.all()
        attendances = Attendance.objects.all()
        for i in range(0, len(classcourse)):
            _Attendances = []
            newClasscourse = ClassCourse(id=classcourse[i].id,
                                         Class_id=classcourse[i].Class_id, Course_id=classcourse[i].Course_id,
                                         Trainer_id=trainer[rnd.randrange(0, len(trainer))].id)
            self._Classcourse.append(newClasscourse)
            listLesson = newClasscourse.Course.lessons_set.all().order_by('Session')
            for j in range(0, len(listLesson)):
                _Attendances.append(attendances.filter(ClassCourse_id=newClasscourse.id, Lesson__id=listLesson[j].id).first())

            a = 0
            slot_id = slots[rnd.randrange(0, len(slots))].id
            classroom_id = classrooms[rnd.randrange(0, len(classrooms))].id
            StartTime = data[3] + timedelta(days=rnd.randrange(0, 7))
            _StartTime = []
            if data[2] != 1:
                for k in range(0, data[2]):
                    StartTime = StartTime + \
                                timedelta(days=rnd.randrange(
                                    0, round(7 / int(data[2]))))
                    while date.weekday(StartTime) == 6:
                        StartTime = StartTime + \
                                    timedelta(days=rnd.randrange(0, 7))
                    _StartTime.append(StartTime)
                _StartTime.sort()
                StartTime = _StartTime[0]
            students = Students.objects.filter(Class_id=newClasscourse.Class_id)
            for j in range(0, len(_Attendances)):
                for k in range(0, len(students)):
                    while date.weekday(StartTime) == 6:
                        StartTime = StartTime + timedelta(days=rnd.randrange(0, 7))
                    newAttendance = Attendance(Student_id=students[k].id,
                                               Lesson_id=_Attendances[j].Lesson_id,
                                               ClassCourse_id=newClasscourse.id,
                                               Date=StartTime,
                                               Slot_id=slot_id,
                                               ClassRoom_id=classroom_id)
                    self._Attendance.append(newAttendance)
                if data[2] == 1:
                    StartTime = StartTime + timedelta(days=7)
                else:
                    a += 1
                    if a == data[2]:
                        a = 0
                        for k in range(0, data[2]):
                            _StartTime[k] = _StartTime[k] + timedelta(days=7)
                    StartTime = _StartTime[a]
        return self

    def calculate(self):
        self._numbOfConflictsAttendance = 0
        self._numbOfConflictsClasscourse = 0
        attendances = self.get_Attendance()
        Attendances = Attendance.objects.all()
        classcourse = self.get_Classcourse()
        for i in range(0, len(attendances)):
            for j in range(0, len(Attendances)):
                if(j >= i):
                    if(attendances[i].Date == Attendances[j].Date and attendances[i].ClassCourse.Trainer_id == Attendances[j].ClassCourse.Trainer_id and attendances[i].ClassCourse_id != Attendances[j].ClassCourse_id  and attendances[i].id != Attendances[j].id):
                        if(attendances[i].ClassRoom_id == Attendances[j].ClassRoom_id and attendances[i].Slot_id == Attendances[j].Slot_id):
                            self._numbOfConflictsAttendance += 1
            for j in range(0, len(attendances)):
                if(j >= i):
                    if(attendances[i].Date == attendances[j].Date and  attendances[i].ClassCourse.Trainer_id == attendances[j].ClassCourse.Trainer_id and attendances[i].ClassCourse_id == attendances[j].ClassCourse_id  and attendances[i].id != attendances[j].id):
                        if(attendances[i].ClassRoom_id == attendances[j].ClassRoom_id and attendances[i].Slot_id == attendances[j].Slot_id):
                            self._numbOfConflictsAttendance += 1
        for i in range(0, len(classcourse)):
            for j in range(0, len(classcourse)):
                if(j >= i):
                    if(classcourse[i].id != classcourse[j].id):
                        if (classcourse[i].Trainer.id == classcourse[j].Trainer.id):
                            self._numbOfConflictsClasscourse += 1
        return [1 / (1.0 * self._numbOfConflictsAttendance + 1), 1 / (1.0 * self._numbOfConflictsClasscourse + 1)]

    def __str__(self):
        returnValueAttendance = ""
        returnValueClasscourse = ""
        for i in range(0, len(self._Attendance)-1):
            returnValueAttendance += str(self._Attendance[i]) + ", "
        for i in range(0, len(self._Classcourse)-1):
            returnValueClasscourse += str(self._Classcourse[i]) + ", "
        return [returnValueClasscourse, returnValueAttendance]


class Population:
    def __init__(self, size, data):
        self._size = size
        self._schedules = []
        for i in range(0, size):
            self._schedules.append(Schedule().initialize(data))

    def get_schedules(self): return self._schedules


class GeneticAlgorithm:
    def evolve(self, population, data):
        return self._mutate_population(self._crossover_population(population, data), data)

    def _crossover_population(self, pop, data):
        crossover_pop = Population(0, data)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPULATION_SIZE:
            schedule1 = self._select_tournament_population(
                pop, data).get_schedules()[0]
            schedule2 = self._select_tournament_population(
                pop, data).get_schedules()[0]
            crossover_pop.get_schedules().append(
                self._crossover_schedule(schedule1, schedule2, data))
            i += 1
        return crossover_pop

    def _mutate_population(self, population, data):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i], data)
        return population

    def _crossover_schedule(self, schedule1, schedule2, data):
        crossoverSchedule = Schedule().initialize(data)
        for i in range(0, len(crossoverSchedule.get_Attendance())):
            if(rnd.random() > 0.5):
                crossoverSchedule.get_Attendance(
                )[i] = schedule1.get_Attendance()[i]
            else:
                crossoverSchedule.get_Attendance(
                )[i] = schedule2.get_Attendance()[i]
        return crossoverSchedule

    def _mutate_schedule(self, mutateSchedule, data):
        schedule = Schedule().initialize(data)
        for i in range(0, len(mutateSchedule.get_Attendance())):
            if(MUTATION_RATE > rnd.random()):
                mutateSchedule.get_Attendance(
                )[i] = schedule.get_Attendance()[i]
        return mutateSchedule

    def _select_tournament_population(self, pop, data):
        tournament_pop = Population(0, data)
        i = 0
        while i < TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(
                pop.get_schedules()[rnd.randrange(0, POPULATION_SIZE)])
            i += 1
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop
