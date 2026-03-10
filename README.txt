Projet Django GalsenArduino

1. Créer un environnement virtuel et l'activer
   python3 -m venv venv
   venv\Scripts\activate  (Windows)
   source venv/bin/activate (Linux/Mac)

2. Installer Django
   pip install django

3. Aller dans le dossier du projet
   cd galsenarduino_project

4. Appliquer les migrations
   python manage.py makemigrations
   python manage.py migrate
   

   
   si ca ne marche pas install Pillow
   python3 -m pip install Pillow

5. Créer un super utilisateur
   python manage.py createsuperuser

6. Lancer le serveur
   python manage.py runserver

7. Accéder au site
   http://127.0.0.1:8000/

8. Accéder à l'admin
   http://127.0.0.1:8000/admin/

pip install django-ckeditor

