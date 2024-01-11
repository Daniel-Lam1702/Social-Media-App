# DoorC Backend
This is the backend for the social media web application for college students called DoorC <br>
Python version: 3.11.4 <br>
Framework: Django <br>
Database: Firebase Cloud Firestore <br>
## Setting up the project locally
1. Go to the command prompt and cd to the directory where you want the project to be stored. Run this command line: <br>
```
git clone https://github.com/Daniel-Lam1702/Social-Media-App-Backend.git
```
2. ```cd Social-Media-App-Backend```
3. Open it on an IDE.
4. Run ```.\myvenv\Scripts\Activate.ps1``` in the command line to run the venv.
5. Run ```pip install -r requirements.txt```to download the libraries used for this project.
6. Create a **.env** file in the **backend** folder. Ask me for the keys privately.
7.```cd backend``` to change to the **backend** folder
8. Run ```python manage.py runserver``` to start running the project
9. To add a new django app run ```python manage.py startapp "name_of_app"```
## Functions Completed, but further testing required
- Users
  - UsernameExists
  - SignUp
  - SendEmailToResetPassword
  - DeleteUser
- Forums
  - CreateForum
  - ToggleForumPrivacy
  - ChangeForumName
  - DeleteForum
- Posts
  - CreatePost (Creating the subcollection Survey is not working yet)
  - GetDraftsFromUser
