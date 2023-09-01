import csv, os
from pathlib import Path
from collections import defaultdict

from models.group import Group, GroupCategory


# Creates the file and writes the headers to the file
def fileCreate(fileName, headers=None):
   path = str(Path.home() / "Downloads" / fileName)
   f = os.open(path, os.O_RDWR | os.O_CREAT, 0o666)
   fd = os.fdopen(f, "x", newline='')
   writer = csv.writer(fd)
   writer.writerow(headers)
   return writer


# EXPORT-GROUPS------------------------------------------------------------------------

def exportGroupCSVModels(course):
   courseName = course.name
   fileName = '{}-Groups.csv'.format(courseName)
   headers = ["studentName", "studentId", "groupCategory", "groupName"]
   writer = fileCreate(fileName, headers)

   groups = course.getGroups()
   for group in groups:
      groupName = group.name
      categoryName = group.data.get('group_category_name')
      
      members = group.getMembers()
      if members:
         for member in members:
            writer.writerow([member.name, member.id, categoryName, groupName])
      else:
         writer.writerow(['', '', categoryName, groupName])
   
   return 'success'


# IMPORT-GROUPS------------------------------------------------------------------------

def importGroups(course, file, canvasapi):
   courseID = course.id
   csvfile  = file.stream.read().decode('utf-8').splitlines()
   input_file = csv.DictReader(csvfile)

   fieldnames = input_file.fieldnames

   if fieldnames[1] == "studentId" and fieldnames[2] == "groupCategory" and fieldnames[3] == "groupName":
      groupsToUpdate = defaultdict(list)     # {groupID: studentID[]}
         
      for row in input_file:

         studentID = row.get('studentId')
         groupCategoryID = row.get('groupCategory')
         groupName = row.get('groupName')

         # groupCategory
         categoryModel = course.getGroupCategory(groupCategoryID)
         if categoryModel is None:
            response = canvasapi.course.create_group_category(courseID, groupCategoryID)
            categoryModel = GroupCategory(response)
            course.addGroupCategory(categoryModel)
            groupCategoryID = response.get('id')
         else:
            groupCategoryID = categoryModel.id
   
         # groupName
         groupModel = categoryModel.getGroup(groupName)
         if groupModel is None:
            response = canvasapi.group.create_group_in_category(groupCategoryID, name=groupName)
            groupModel = Group(response)
            categoryModel.addGroup(groupModel)
            groupID = response.get('id')
         else:
            groupID = groupModel.id

         if studentID:
            groupsToUpdate[groupID].append(studentID)

      for group in groupsToUpdate:
         members = groupsToUpdate[group]
         canvasapi.group.edit(groupID, members=members)

      return 'success'
   else:
      return 'Incorrect field names'
