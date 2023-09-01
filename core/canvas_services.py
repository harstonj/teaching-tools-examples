import json
import os, csv, wget
from flask import jsonify

# Canvas Functions
import canvasFunctions.assignments
import canvasFunctions.courses
import canvasFunctions.quizzes
import canvasFunctions.settings
import canvasFunctions.students
import canvasFunctions.syllabus
import canvasFunctions.pages
from canvasFunctions.util import getDictSubset, getSubset

# Models
from models.assignment import Assignment
from models.course import Course
from models.folder import Folder, File
from models.group import Group, GroupCategory
from models.page import Page
from models.quiz import Quiz
from models.user import User

# Canvas API
from canvasAPI.canvas import Canvas
from canvasAPI.util import depaginate


class canvas_services:
    """
    The main class to be instantiated to perform Canvas operations and to 
    provide access to Canvas's API.
    """

    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the Canvas instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: json
        """

        self.canvasapi = Canvas(base_url, access_token)


    ### EXAMPLE METHODS ###
    # ---COURSES----------------------------------------------------------------
    
    def getCourseData(self, courseID, **kwargs):
        """ return the data for a given course """
        response = self.canvasapi.course.get_course(courseID, **kwargs)
        return response
    
    def getCourse(self, courseID, **kwargs):
        """ retrieve data from canvas api and return a course model """
        response = self.canvasapi.course.get_course(courseID, **kwargs)
        return Course(response)

    def getCoursesData(self, subset=None, **kwargs):
        """
        Return a list of courses data for the current user.
        If a subset is included in the args, it will return a list of
        course dictionaries with subset key values.
        Example: subset = ('name', 'id')
        Return: [{'name': value, 'id': value}] 
        """
        coursePagList = self.canvasapi.course.get_courses(**kwargs)
        
        courseList = []
        for item in coursePagList:
            if item.get('name') is not None:
                if subset:
                    courseList.append(getDictSubset(item, subset))
                else:
                    courseList.append(item)
        return courseList

    def getCourses(self, **kwargs):
        """
        Return a list of active courses as course model objects.
        """
        coursePagList = self.canvasapi.course.get_courses(**kwargs)
        
        courses = []
        for item in coursePagList:
            if item.get('name') is not None:
                courses.append(Course(item))
        return courses
        
    def getFavorites(self, subset=None, **kwargs):
        """
        Retrieve a list of favorited courses for the current user.
        If a subset is included in the args, it will return a list of
        course dictionaries with subset key values.
        Example: subset = ('name', 'id')
        Return: [{'name': value, 'id': value}]
        """
        coursePagList = self.canvasapi.course.get_favorites(**kwargs)

        favorites = []
        for item in coursePagList:
            if item.get('name') is not None:
                if subset:
                    favorites.append(getDictSubset(item, subset))
                else:
                    favorites.append(item)
        return favorites

    # ---STUDENTS---------------------------------------------------------------

    def getStudentsData(self, courseID, **kwargs):
        """ returns a list of students data in a course """
        studentPagList = self.canvasapi.course.get_users(courseID, enrollment_type='student', **kwargs)
        students = depaginate(studentPagList)
        return students

    def getStudents(self, courseID, **kwargs):
        """ returns a list of student User model objects """
        return self.getUsers(courseID, enrollment_type='student', **kwargs)

    def getUsersData(self, courseID, **kwargs):
        """ returns a list of students data in a course """
        userPagList = self.canvasapi.course.get_users(courseID, **kwargs)
        users = depaginate(userPagList)
        return users
    
    def getUsers(self, courseID, **kwargs):
        """ 
        Returns a list of User model objects
        """
        userPagList = self.canvasapi.course.get_users(courseID, **kwargs)
        userList = []
        for item in userPagList:
            user = User(item)
            userList.append(user)
        return userList

    def getUserData(self, userID="self", **kwargs):
        """ return the data for a specific user by ID or `self` """
        user = self.canvasapi.user.get_user(userID, **kwargs)
        return user

    # ---GROUPS-----------------------------------------------------------------

    def getGroupsData(self, courseID, **kwargs):
        """ returns a list of groups data for a course """
        groupPagList = self.canvasapi.course.get_groups(courseID, **kwargs)
        groups = depaginate(groupPagList)
        return groups
    
    def getGroups(self, courseID, **kwargs):
        """ returns a list of group model objects """
        groupPagList = self.canvasapi.course.get_groups(courseID, **kwargs)
        itemList = []
        for item in groupPagList:
            item = Group(item)
            itemList.append(item)
        return itemList
    
    def getGroupsCategories(self, courseID, **kwargs):
        """ 
        returns a list of GroupCategory models with a dictionary
        of Group models
        """
        categoryPagList = self.canvasapi.course.get_group_categories(courseID, **kwargs)
        catList = []
        for cat in categoryPagList:
            category = GroupCategory(cat)
            catList.append(category)
            groupPagList = self.canvasapi.group.get_groups_in_category(category.id)
            for group in groupPagList:
                group = Group(group)
                group.setCategoryName(cat)
                category.addGroup(group)
        return catList

    def getGroupsList(self, courseID):
        """ returns a list of group dictionaries with the keys: 'name', 'id'
        """
        groups = self.getGroupsData(courseID)
        groupsList = []
        for group in groups:
            entry = {'name': group.get('name'), 'id': group.get('id')}
            groupsList.append(entry)
        return groupsList

    def exportGroupsJSON(self, courseID, key='name'):
        """ exports a JSON of all groups and their members with a given key """
        course = self.getGroupMembers(courseID)
        if key == "":
            key = 'name'
        subset = ('id', key)
        groupsJson = {}
        for group in course.getGroups():
            members = [member.getDictSubset(subset) for member in group.getMembers()]
            groupsJson[group.name] = members
        return groupsJson

    def exportGroupsCSV(self, courseID):
        """ Creates a csv file of students and their groups 
            from a specified course
        """
        course = self.getGroupMembers(courseID, getGroupCategory=True)
        return canvasFunctions.students.exportGroupCSVModels(course)

    def getGroupMembers(self, courseID, getGroupCategory=False):
        """ Gets all students and their groups from a specified course and
            saves the data to a course model
        """
        course = self.getCourse(courseID)
        students = self.getStudents(courseID)
        course.addStudents(students)
        groupPagList = self.canvasapi.course.get_groups(courseID)
        for item in groupPagList:
            group = Group(item)
            course.addGroup(group)
            if getGroupCategory:
                groupCategoryId = group.get('group_category_id')
                if groupCategoryId:
                    category = self.canvasapi.group.get_group_category(groupCategoryId)
                    group.setCategoryName(category)
            memberPagList = self.canvasapi.group.get_users(group.get('id'))
            for user in memberPagList:
                memberID = user.get('id')
                member = course.getStudentById(memberID)
                group.addMember(member)
        return course

    def importStudentGroups(self, courseID, file):
        course = self.getCourse(courseID)
        groupCategories = self.getGroupsCategories(courseID)
        for category in groupCategories:
            course.addGroupCategory(category)

        response = canvasFunctions.students.importGroups(course, file, self.canvasapi)
        return response

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    canvas_services.main()
