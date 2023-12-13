import os, json, shutil

print('''
$$$$$$$$\ $$$$$$$$\  $$$$$$\         $$$$$$\                                $$\                           $$$$$$$$\                  $$\ $$\       $$\   $$\     
$$  _____|\__$$  __|$$  __$$\       $$  __$$\                               \__|                          \__$$  __|                 $$ |$$ |      \__|  $$ |    
$$ |         $$ |   $$ /  \__|      $$ /  \__| $$$$$$\   $$$$$$\ $$\    $$\ $$\  $$$$$$$\  $$$$$$\           $$ | $$$$$$\   $$$$$$\  $$ |$$ |  $$\ $$\ $$$$$$\   
$$$$$\       $$ |   \$$$$$$\        \$$$$$$\  $$  __$$\ $$  __$$\\$$\  $$  |$$ |$$  _____|$$  __$$\          $$ |$$  __$$\ $$  __$$\ $$ |$$ | $$  |$$ |\_$$  _|  
$$  __|      $$ |    \____$$\        \____$$\ $$$$$$$$ |$$ |  \__|\$$\$$  / $$ |$$ /      $$$$$$$$ |         $$ |$$ /  $$ |$$ /  $$ |$$ |$$$$$$  / $$ |  $$ |    
$$ |         $$ |   $$\   $$ |      $$\   $$ |$$   ____|$$ |       \$$$  /  $$ |$$ |      $$   ____|         $$ |$$ |  $$ |$$ |  $$ |$$ |$$  _$$<  $$ |  $$ |$$\ 
$$ |         $$ |   \$$$$$$  |      \$$$$$$  |\$$$$$$$\ $$ |        \$  /   $$ |\$$$$$$$\ \$$$$$$$\          $$ |\$$$$$$  |\$$$$$$  |$$ |$$ | \$$\ $$ |  \$$$$  |
\__|         \__|    \______/        \______/  \_______|\__|         \_/    \__| \_______| \_______|         \__| \______/  \______/ \__|\__|  \__|\__|   \____/

   ____    __              ____        _      __ 
  / __/__ / /___ _____    / __/_______(_)__  / /_
 _\ \/ -_) __/ // / _ \  _\ \/ __/ __/ / _ \/ __/
/___/\__/\__/\_,_/ .__/ /___/\__/_/ /_/ .__/\__/ 
                /_/                  /_/
      
Rev: 0.0.1
Build: 202312130.0.1
Created By: Everly Larche
      ''')

ans = input ('Would you like to automatically setup the service toolkit application and its dependencies? (y/n)')
if ans != ('y' or 'Y'): exit()

print('''
\n
By defualt this script will do the following:
1. Copy the required files into a folder on your C:\FTSserviceToolkit on Windows or ~/FTSserviceToolkit on Unix.
2. Install WKHTMLTOPDF PDF conversion engine.
3. Create a desktop shortcut.
4. Create a start menue link (Windows only).
5. Remove the setup files.
      ''')

print('Copying files...')
os.mkdir(os.path.join('FTSserviceToolkit'))

print('Installing WKHTMLTOPDF and updating config file with its location')