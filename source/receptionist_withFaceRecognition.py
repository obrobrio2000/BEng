from robot_cmd_ros import *
import face_recognition

begin()


class Person:
    def __init__(self, face, name, gender, pronouns, drink):
        self.face = face
        self.name = name
        self.gender = gender
        self.pronouns = pronouns
        self.drink = drink


yes = ['yes', 'Yes', 'YES', 'Yeah', 'yeah', 'Yep',
       'yep', 'YEP', 'Correct', 'correct', 'Right', 'right']
no = ['no', 'No', 'Nope', 'nope', 'Wrong', 'wrong']

maleGender = ['male', 'mail', 'man', 'men', 'boy',
              'guy', 'Male', 'Mail', 'Man', 'Men', 'Boy', 'Guy']
femaleGender = ['female', 'woman', 'women', 'girl',
                'gal', 'Female', 'Woman', 'Women', 'Girl', 'Gal']

# Create the haar cascade
faceCascade = findCascadeModel()

helperName = "John"
helperFaceJPG = 'helper.jpg'


def getImageJPG():
    getImage()
    return os.getenv('MARRTINO_APPS_HOME') + "/www/viewer/img/lastimage.jpg"


seatsQueue = ["seat0", "seat1", "seat2"]


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


def pointToPerson(knownFaceJPG):
    guestFound = False
    while (guestFound == False):
        known_image = face_recognition.load_image_file(knownFaceJPG)
        unknown_image = face_recognition.load_image_file(getImageJPG())
        known_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        if face_recognition.compare_faces([known_encoding], unknown_encoding) == True:
            guestFound = True
            break
        left(1)


faces = []
facesJPG = []

guests = []

while (faces == []):
    # Read the image
    image = cv2.imread(getImageJPG(), 0)
    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    # Crop the faces
    for (x, y, w, h) in faces:
        facesJPG.append(image[y:y+h, x:x+w])

for faceJPG in facesJPG:
    # Displays the face of the current guest
    # display(faceJPG)
    # Ask name
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
    # Ask gender
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
    # Ask favorite drink
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
    # Create person
    person = Person(faceJPG, name, gender, drink)
    # Add person to guests list
    guests.append(person)
    # Go to helper
    say("Okay, " + name + ", please follow me.")
    goToSpecificTarget("helper")
    # Introduce guest to helper
    say("Hi " + helperName + "! This is our new guest!", language='en')
    # Point to guest
    pointToPerson(faceJPG)
    say(pronouns.split("/")[2] + " name is " + name + " and " + pronouns.split("/")[2] + " favorite drink is " +
        drink + ".", language='en')
    # Point to helper
    pointToPerson(helperFaceJPG)
    say("I'll now bring " + pronouns.split("/")
        [1] + " to an empty seat!", language='en')
    # Point to guest
    pointToPerson(faceJPG)
    # Go to the seats room
    say("Please follow me to the seats room.", language='en')
    goToSpecificTarget("seat0")
    say("There you go, " + name +
        "! Let's see if there is an empty seat for you!", language='en')
    emptySeat = False
    seatPointing = "seat0"
    while emptySeat == False:
        image = getImageJPG()
        tagFound = tagTrigger(image)
        if tagFound == True:
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
