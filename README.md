# Teaching Tools

## The Project

Canvas is a website used by instructors and students at UWB to access and manage their courses. Teaching Tools is an application in the early stages of development that integrates with Canvas to provide more functionality for students and faculty. For my computer science and software engineering degree capstone project I contributed to this application by refactoring the back-end Python code. I redesigned the architecture to improve the logic and flow of the program and remove redundancies. I wanted to provide a simple way to access the Canvas API so I added an API wrapper which encapsulates a substantial number of Canvas API calls into a single service. This will help streamline the process of interacting with Canvas and allow for new features to be implemented more quickly. In addition, I created a pure data model layer that stores the data retrieved from Canvas so the data can be more easily processed.

## The Code
This is some example code from the project that I refactored and developed. 

The Canvas API wrapper is modeled from the [ufcopen/canvasapi](https://github.com/ucfopen/canvasapi) library, however I removed the storage of data in the wrapper and created a new canvasAPI interface (canvas.py).

The original unit tests were performed on the live data from Canvas, so I created unit tests that make mock API calls and returns unchanging data from a file for comparison.
