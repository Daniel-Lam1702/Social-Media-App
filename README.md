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
2. Run: <br>
```
cd Social-Media-App-Backend
```
Or open the project on an IDE.
3. Run in the command line to run the venv: <br>
```
.\myvenv\Scripts\Activate.ps1
```
4. Run to download the libraries used for this project: <br>
```
pip install -r requirements.txt
```
5. Create a **.env** file in the **backend** folder. Ask me for the keys privately.
6. To change to the **backend** folder run: <br>
```
cd backend
``` 
7. To start running the project: <br>
```
python manage.py runserver
```
8. To add a new django app run: <br>
```
python manage.py startapp "name_of_app"
```
9. If you installed a new library run: <br>
```
pip freeze > requirements.txt
```
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
## API Documentation:
https://docs.google.com/document/d/13NXs6NUCFribgJqT2ICyjAQVXwi-IqH_NfCbnopWPKo/edit?usp=sharing
