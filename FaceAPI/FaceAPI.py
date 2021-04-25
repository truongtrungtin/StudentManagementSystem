import glob
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw
from StudentManagementSystem import settings
import time
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from .FireBase import StorageImage

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
os.environ['FACE_SUBSCRIPTION_KEY'] = '1a47395ea9154b018fa454b27045003b'

os.environ['FACE_ENDPOINT'] = 'https://attendancesystems.cognitiveservices.azure.com/'

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
KEY = os.environ['FACE_SUBSCRIPTION_KEY']

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.environ['FACE_ENDPOINT']

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))


# Used in the Person Group Operations,  Snapshot Operations, and Delete Person Group examples.
# You can call list_person_groups to print a list of preexisting PersonGroups.
# SOURCE_PERSON_GROUP_ID should be all lowercase and alphanumeric. For example, 'mygroupname' (dashes are OK).
PERSON_GROUP_ID = 'students'

# Used for the Snapshot and Delete Person Group examples.
# TARGET_PERSON_GROUP_ID = str(uuid.uuid4()) # assign a random ID (or name it anything)

'''
Create the PersonGroup
'''
# Create empty Person Group. Person Group ID must be lower case, alphanumeric, and/or with '-', '_'.
# print('Person group:', PERSON_GROUP_ID)
# face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)


def DeleteImage(Url, personId, faceId):
    StorageImage.Delete(Url)
    face_client.person_group_person.delete_face(
        PERSON_GROUP_ID, personId, faceId)
    print(f'Delete face success')


def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    return left - 20, top - 25, right + 20, bottom + 10


def AddImageforStudent(Username, personId):
    types = ('*.jpg', '*.png')
    person = face_client.person_group_person.get(PERSON_GROUP_ID, personId)
    for type in types:
        # Find all jpeg images of friends in working directory
        images = [file for file in glob.glob('{}/staticmedia/ImageStudent/{}/{}'.format(settings.BASE_DIR, Username, type))]
        if images is None:
            print('No find image')
            continue
        # Add to a woman person
        for image in images:
            img = open(image, 'r+b')
            faceid = face_client.person_group_person.add_face_from_stream(
                PERSON_GROUP_ID, person.person_id, img)
            print(
                f'Add image {image} Success for person id: {person.person_id}')
            if len(images) > 1:
                time.sleep(4)


def CheckGroup():
    faceGroup = face_client.person_group.list()
    if faceGroup.__len__() > 0:
        if faceGroup[0].person_group_id != PERSON_GROUP_ID:
            face_client.person_group.create(
                person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)
    else:
        face_client.person_group.create(
            person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)


def SubmitStudent(Username):
    CheckGroup()
    person = face_client.person_group_person.create(PERSON_GROUP_ID, Username)
    return person.person_id


def DeleteStudent(person_id):
    face_client.person_group_person.delete(
        person_group_id=PERSON_GROUP_ID, person_id=person_id)


# Students = ['trungtin','thuyhanh']
# SubmitStudent(Students)

# Train PersonGroup
# '''
def TrainPersonGroup():
    # Train the person group
    face_client.person_group.train(PERSON_GROUP_ID)

    # while (True):
    #     training_status = face_client.person_group.get_training_status(
    #         PERSON_GROUP_ID)
    #     print("Training status: {}.".format(training_status.status))
    #     if (training_status.status is TrainingStatusType.succeeded):
    #         break
    #     elif (training_status.status is TrainingStatusType.failed):
    #         sys.exit('Training the person group has failed.')
        # time.sleep(4)


def dectect(ClassRoom):
    types = ('*.jpg', '*.png')
    faceIds = []
    for type in types:
        # Find all jpeg images of friends in working directory
        images = [file for file in glob.glob(StorageImage.GetImage(
            'media/ClassRoom/{}/{}'.format(ClassRoom, type)))]
        if len(images) == 0:
            print('No find image')
            continue

        for img in images:

            IMAGES_FOLDER = os.path.join(
                os.path.dirname(os.path.realpath(__file__)))

            # Get test image
            test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, img))
            image = open(test_image_array[0], 'r+b')
            img = Image.open(test_image_array[0])

            faces = face_client.face.detect_with_stream(image)

            if len(faces) > 0:
                for faceid in faces:
                    faceIds.append(faceid.face_id)
                    # print(f'Found {len(faces)} faces.')
    return faceIds

# Identify faces


def identify(faceIds):
    if len(faceIds) == 0:
        print('No person identified in the person group for faces from .')
        return
    results = face_client.face.identify(faceIds, PERSON_GROUP_ID)

    return results


def recognize(ClassRoom):
    detectedFaces = dectect(ClassRoom)
    if (len(detectedFaces) == 0):
        print("Can't detect any face")
        return

    identifiedResult = identify(detectedFaces)

    allStudent = face_client.person_group_person.list(PERSON_GROUP_ID)
    listStudent = []
    for i in identifiedResult:
        # print('Identifying faces id {}'.format(i.face_id))
        for s in allStudent:
            if i.candidates[0].person_id == s.person_id:
                listStudent.append(s.name)
            continue
    # print(listStudent)
    return listStudent

# ************+************+************+************+************+************+************+************+************+************+


def saveImageClassroom(Class, Course, lesson, Img):
    img = Image.open(Img)
    # StorageImage.saveImageClassroom(f'ClassRoom/{Class}/{Course}/{lesson}',Img)
    if os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}'):
        img.save(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/class.png', 'PNG')
    else:
        if not os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom'):
            os.mkdir(f'{settings.BASE_DIR}/static/media/ClassRoom')
        if not os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}'):
            os.mkdir(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}')
        if not os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}'):
            os.mkdir(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}')
        if not os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}'):
            os.mkdir(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}')
        img.save(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/class.png', 'PNG')


def dectectClassImages(Class, Course, lesson):
    types = ('*.jpg', '*.png')
    faceIds = []
    listStudent = []
    for type in types:
        # files = StorageImage.storage.ref('ClassRoom/{}/{}/{}/'.format(Class, Course, lesson))
        # for file in files:
        #     c = StorageImage.storage.child(file.name).get_url(None)
        # images = [file for file in glob.glob(StorageImage.storage.child('ClassRoom/{}/{}/{}/{}'.format(Class, Course, lesson, type)))]
        images = [file for file in glob.glob('{}/static/media/ClassRoom/{}/{}/{}/{}'.format(settings.BASE_DIR, Class, Course, lesson, type))]

        if len(images) == 0:
            continue

        for img in images:

            IMAGES_FOLDER = settings.BASE_DIR

            # Get test image
            test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, img))
            image = open(test_image_array[0], 'r+b')
            img = Image.open(test_image_array[0])
            faces = face_client.face.detect_with_stream(image)

            if len(faces) == 0:
                continue
            for face in faces:
                faceIds.append(face.face_id)
            identifiedResult = identifyClass(faceIds)
            allStudent = face_client.person_group_person.list(PERSON_GROUP_ID)
            for face in faces:
                for i in identifiedResult:
                    for s in allStudent:
                        if i.candidates[0].person_id == s.person_id:
                            if len(i.candidates) > 0:
                                if i.face_id == face.face_id:
                                    listStudent.append(s.name)
                                    cut = img.crop(getRectangle(face))
                                    if os.path.exists(f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/faces/'):
                                        cut.save(
                                            f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/faces/{s.name}.png', 'PNG')
                                    else:
                                        os.mkdir(
                                            f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/faces/')
                                        cut.save(
                                            f'{settings.BASE_DIR}/static/media/ClassRoom/{Class}/{Course}/{lesson}/faces/{s.name}.png', 'PNG')
        return listStudent
                # StorageImage.saveImageClassroom(f'media/ClassRoom/{Class}/{Course}/{lesson}/faces/{face.face_id}.png', cut)


def dectectClass(Class, Course, lesson):
    types = ('*.jpg', '*.png')
    faceIds = []
    for type in types:
        # Find all jpeg images of friends in working directory
        images = [file for file in glob.glob('{}/static/media/ClassRoom/{}/{}/{}/faces/{}'.format(settings.BASE_DIR,Class, Course, lesson, type))]
        if len(images) == 0:
            print('No find image')
            continue

        for img in images:

            IMAGES_FOLDER = settings.BASE_DIR

            # Get test image
            test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, img))
            image = open(test_image_array[0], 'r+b')

            faces = face_client.face.detect_with_stream(image)

            if len(faces) > 0:
                for faceid in faces:
                    faceIds.append(faceid.face_id)
            # print(f'Found {len(faces)} faces.')
    return faceIds

# Identify faces


def identifyClass(faceIds):
    if len(faceIds) == 0:
        print('No person identified in the person group for faces from .')
        return

    results = face_client.face.identify(faceIds, PERSON_GROUP_ID)

    return results


def recognizeclass(Class, Course, lesson):
    detectedFaces = dectectClass(Class, Course, lesson)
    if (len(detectedFaces) == 0):
        print("Can't detect any face")
        return
    identifiedResult = identifyClass(detectedFaces)

    allStudent = face_client.person_group_person.list(PERSON_GROUP_ID)

    listStudent = []
    for i in identifiedResult:
        # print('Identifying faces id {}'.format(i.face_id))
        if len(i.candidates) > 0:
            for s in allStudent:
                if i.candidates[0].person_id == s.person_id:
                    listStudent.append(s.name)
    return listStudent

# print(dectectClassImages('2007-detech-20-07-2020'))
# print(recognizeclass('2007-detech-20-07-2020'))

