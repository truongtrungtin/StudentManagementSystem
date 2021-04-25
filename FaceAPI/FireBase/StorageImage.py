import pyrebase


config = {
    "apiKey": "AIzaSyBbDcHUidhKq2DBBQXNFTAnkVgPjkpnXBA",
    "authDomain": "image-4bfb0.firebaseapp.com",
    "databaseURL": "https://image-4bfb0-default-rtdb.firebaseio.com",
    "projectId": "image-4bfb0",
    "storageBucket": "image-4bfb0.appspot.com",
    "serviceAccount": "serviceAccountKey.json",
}


firebase_storage = pyrebase.initialize_app(config)

auth = firebase_storage.auth()
user = auth.sign_in_with_email_and_password("a00.n0reply@hotmail.com", "Tinpro123")



def SaveImage(id,image,url):
    storage = firebase_storage.storage()
    storage.child('{0}/{1}/{2}'.format(url, id, image.name)).put(image, image.content_type)
    return storage.child('{0}/{1}/{2}'.format(url, id, image.name)).path

def saveImageClassroom(url, img):
    storage = firebase_storage.storage()
    storage.child(url).put(img, str(img.size))
    a = storage.child(url)
    return a.path

def GetImageDefaultAvatar():
    storage = firebase_storage.storage()
    return storage.child('Avatar/default.png').path

def GetImage(url):
    storage = firebase_storage.storage()
    a = storage.child(url)
    return a.get_url(None)

def Delete(url):
    storage = firebase_storage.storage()
    storage.delete(url)
