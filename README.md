# Script Kobo - Zendro

Este script recoge datos de los formularios de KoboToolBox para insertarlos en el modelo de despliegues de Zendro. Para iniciar este script es necesario tener intalado python 3.8 o superior, y los requirements que se encuentran en requirements.txt

    pip install -r requirements.txt

También es necesario establecer algunas variables de ambiente en un archivo .env, en el root del proyecto:

    # Kobo credentials
    KOBO_USER=kobo_user
    KOBO_PASSWORD=kobo_password 

    # Zendro credentials
    ZENDRO_URL="[zendro url]"
    ZENDRO_USER=zendro_user  
    ZENDRO_PASSWORD=zendro_password

una vez listo esto el script se puede correr como cualquier script de python: `python main.py` 