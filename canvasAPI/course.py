from .canvas_object import CanvasObject
from .paginated_list import PaginatedList
from .exceptions import RequiredFieldMissing
from .upload import Uploader, FileOrPathLike
from .util import combine_kwargs


class Course(CanvasObject):

   def get_course(self, course_id, **kwargs):
      """
      Retrieve a course by its ID.
      :calls: `GET /api/v1/courses/:id \
      <https://canvas.instructure.com/doc/api/courses.html#method.courses.show>`_
      :param course_id: The ID of the course to retrieve.
      :type course: int
      :rtype: dict
      """
      uri_str = "courses/{}"

      response = self._requester.request(
         "GET", uri_str.format(course_id), _kwargs=combine_kwargs(**kwargs)
      )
      return response.json()

   def get_courses(self, **kwargs):
      """
      Return a list of active courses for the current user.
      :calls: `GET /api/v1/courses \
      <https://canvas.instructure.com/doc/api/courses.html#method.courses.index>`_
      :rtype: :class:`canvasAPI.paginated_list.PaginatedList`
      """
      return PaginatedList(
         self._requester, "GET", "courses", _kwargs=combine_kwargs(**kwargs)
      )  

   def get_favorites(self, **kwargs):
      """
      Retrieve a list of favorited courses for the current user
      :calls: GET users/self/favorites/courses
      'https://canvas.instructure.com/doc/api/favorites.html'
      """
      uri = "users/self/favorites/courses"
      
      return PaginatedList(
         self._requester, "GET", uri, _kwargs=combine_kwargs(**kwargs))

   def get_user(self, course_id, user_id, **kwargs):
      """
      Retrieve a user by their ID.
      :calls: `GET /api/v1/courses/:course_id/users/:id \
      <https://canvas.instructure.com/doc/api/courses.html#method.courses.user>`_
      :rtype: dict
      """

      uri = "courses/{}/users/{}".format(course_id, user_id)

      response = self._requester.request("GET", uri, _kwargs=combine_kwargs(**kwargs))
      return response.json()

   def get_users(self, course_id, **kwargs):
      """
      List all users in a course.
      :calls: `GET /api/v1/courses/:course_id/search_users \
      <https://canvas.instructure.com/doc/api/courses.html#method.courses.users>`_
      :rtype: :class:`canvasAPI.paginated_list.PaginatedList`
      """

      return PaginatedList(
         self._requester,
         "GET",
         "courses/{}/search_users".format(course_id),
         _kwargs=combine_kwargs(**kwargs),
      )

   def create_group_category(self, course_id, name, **kwargs):
      """
      Create a group category.
      :calls: `POST /api/v1/courses/:course_id/group_categories \
      <https://canvas.instructure.com/doc/api/group_categories.html#method.group_categories.create>`_
      :param name: Name of the category.
      :type name: str
      :rtype: dict
      """