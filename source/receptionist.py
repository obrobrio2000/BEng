from robot_cmd_ros import *
from time import sleep
import cv2

begin()

class Person:
    def __init__(self, face, name, gender, pronouns, drink):
        self.face = face
        self.name = name
        self.gender = gender
        self.pronouns = pronouns
        self.drink = drink

yes = ['yes', 'Yes', 'YES', 'Yeah', 'yeah', 'Yep', 'yep', 'YEP', 'Correct', 'correct', 'Right', 'right']
no = ['no', 'No', 'Nope', 'nope', 'Wrong', 'wrong']
maleGender = ['male', 'mail', 'man', 'men', 'boy', 'guy', 'Male', 'Mail', 'Man', 'Men', 'Boy', 'Guy']
femaleGender = ['female', 'woman', 'women', 'girl', 'gal', 'Female', 'Woman', 'Women', 'Girl', 'Gal']

# Si preleva il modello Haar Cascade per facce frontali
faceCascade = findCascadeModel()

# Funzione per prelevare l'ultima immagine catturata, in formato JPG
def getImageJPG():
    getImage()
    MARRTINO_APPS_HOME = os.getenv('MARRTINO_APPS_HOME')
    assert MARRTINO_APPS_HOME is not None
    return MARRTINO_APPS_HOME + "/www/viewer/img/lastimage.jpg"

def goToSpecificTarget(target):
    if target == "start":
        gotoTarget(0, 0, frame='map')
    elif target == "helper":
        gotoTarget(0.1, 0.08, frame='map')
    elif target == "seat0":
        gotoTarget(1.1, 0.16, frame='map')
    elif target == "seat1":
        gotoTarget(1.1, 0.24, frame='map')
    elif target == "seat2":
        gotoTarget(1.1, 0.32, frame='map')

faces = [] # Deve avere grandezza pari ad 1, ovvero una faccia alla volta
facesJPG = [] # Stessa condizione dell'array "faces"
guests = [] # Array con unico scopo di logging (memorizzare i profili degli ospiti)
helperName = "John" # Nome dell'helper (nel nostro caso "John")

while (faces == []):
    # Legge l'immagine catturata
    image = cv2.imread(getImageJPG(), 0)
    # Rileva le facce nell'immagine
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    # Handler nel caso di rilevazione di due o piu' facce (vedere Paragrafo 5.2.1)
    if faces > 1:
        say("I see more than one face, please one of you step back. Will check again in 2 seconds.")
        faces = []
        sleep(2)
        continue
    # Ritaglia la faccia e la memorizza in un array
    for (x, y, w, h) in faces:
        facesJPG.append(image[y:y+h, x:x+w])
    # Mostra la faccia dell'ospite (solo su robot provvisti di display)
    display(facesJPG[0])
    # Chiede il nome dell'ospite
    name = ""
    say("Hello, what is your name?", language="en")
    nameIsCorrect = False
    while (nameIsCorrect == False):
        name = asr()
        say("Is " + name + " correct?", language="en")
        if (asr() in yes):
            nameIsCorrect = True
            name = name.capitalize()
        else:
            say("Oh, sorry, I must've heard wrong! Please repeat.", language="en")
    # Chiede il sesso dell'ospite
    gender = ""
    pronouns = ""
    say("How do you identify yourself?", language='en')
    genderIsCorrect = False
    while (genderIsCorrect == False):
        gender = asr()
        if gender in maleGender:
            say('You identify as a male, correct?', language='en')
            if (asr() in yes):
                genderIsCorrect = True
                gender = "male"
                pronouns = "he/him/his"
            else:
                say("Oh, sorry, I must've heard wrong! Please repeat.", language="en")
        elif gender in femaleGender:
            say('You identify as a female, correct?', language='en')
            if (asr() in yes):
                genderIsCorrect = True
                gender = "female"
                pronouns = "she/her/her"
            else:
                say("Oh, sorry, I must've heard wrong! Please repeat.", language="en")
        else:
            say('You identify as non-binary, correct?', language='en')
            if (asr() in yes):
                genderIsCorrect = True
                gender = "non-binary"
                pronouns = "they/them/their"
            else:
                say("Oh, sorry, I must've heard wrong! Please repeat.", language="en")
    # Chiede il drink preferito dell'ospite
    drink = ""
    say("Last question: what's your favorite drink?", language='en')
    drinkIsCorrect = False
    while (drinkIsCorrect == False):
        drink = asr()
        say("Is " + drink + " correct?", language="en")
        if (asr() in yes):
            drinkIsCorrect = True
            drink = drink.capitalize()
        else:
            say("Oh, sorry, I must've heard wrong! Please repeat.", language="en")
    # Crea un oggetto persona attraverso la classe dedicata
    person = Person(facesJPG[0], name, gender, pronouns, drink)
    # Memorizza l'oggetto persona in un array per questioni di logging
    guests.append(person)
    # Il robot va da John
    say("Okay, " + name + ", please follow me. And please always stay on my left.")
    goToSpecificTarget("helper")
    # Controlla se John e' li'
    helperIsThere = False
    while (helperIsThere == False):
        # Read the image
        image = cv2.imread(getImageJPG(), 0)
        # Detect faces in the image
        temp = faces
        faces = faceCascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if faces != []:
            helperIsThere = True
        else:
            say("I can't find the helper, please wait. Will check again in 5 seconds.")
            sleep(5)
        faces = temp
    # Introduzione dell'ospite a John
    say("Hi " + helperName + "! This is our new guest!", language='en')
    # Trova l'ospite (per guardarlo durante l'introduzione)
    left(1)
    say(pronouns.split("/")[2] + " name is " + name + " and " + pronouns.split("/")[2] + " favorite drink is " + drink + ".", language='en')
    # Guarda John
    right(1)
    say("I'll now bring " + pronouns.split("/")
        [1] + " to an empty seat!", language='en')
    # Guarda l'ospite
    left(1)
    # Vai alla stanza dei posti a sedere
    say("Please follow me to the seats room.", language='en')
    goToSpecificTarget("seat0")
    say("There you go, " + name +
        "! Let's see if there is an empty seat for you!", language='en')
    seatPointing = "seat0"
    emptySeat = False
    while emptySeat == False:
        if tagTrigger() == True:
            emptySeat = True
            say("You can sit there! I'll go, you can find me at the reception.", language='en')
            goToSpecificTarget("start")
        if (seatPointing == "seat0"):
            goToSpecificTarget("seat1")
            seatPointing = "seat1"
        elif (seatPointing == "seat1"):
            goToSpecificTarget("seat2")
            seatPointing = "seat2"
        # if all seats checked, tell guest there is no empty seat at the moment
        elif (seatPointing == "seat2"):
            say("There is no empty seat at the moment. You can wait here until another guest stands up. I'll go, you can find me at the reception.", language='en')
            goToSpecificTarget("start")
            break

end()
