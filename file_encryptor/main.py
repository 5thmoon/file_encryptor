# kivy config, must be imported at top of file
from kivy.config import Config

Config.set('graphics', 'resizable', '0')

# python Imports
from plyer import filechooser

# kivy imports
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder

# kivyMD imports
from kivymd.app import MDApp
from kivymd.toast import toast

# local imports
from file_encryptor import encrypt

# set window size
Window.size = (800, 600)
Window.minimum_width, Window.minimum_height = Window.size


# main screen/manager
class MainScreen(ScreenManager):
    pass


# encryption screen
class EncryptScreen(Screen):

    def __init__(self, **kwargs):
        super(EncryptScreen, self).__init__(**kwargs)
        self.salt = None
        self.password = None
        self.key = None
        self.fernet = None

    # called when pressing button, returns key or salt based on switch toggle
    def generate_keyfile(self):
        password = bytes(self.ids.password.text, 'utf-8')
        print(password)
        try:
            if self.ids.switch1.active:
                if password == bytes("", 'utf-8'):
                    toast("Please enter a passphrase")
                else:
                    self.key, self.salt = encrypt.generate_key_password(password)
                    filechooser.save_file(on_selection=self.save_salt_file)
                    print(self.salt)
                    return self.key, self.salt
            else:
                self.key = encrypt.generate_key()
                filechooser.save_file(on_selection=self.save_keyfile)
                return self.key
        except TypeError:
            print("Unicode error")

    # save the keyfile to a location on the drive
    def save_keyfile(self, filename: list):
        try:
            encrypt.write_key_to_file(filename[0], self.key)
        except TypeError:
            return False

    # save the salt to a file in location on drive
    def save_salt_file(self, filename: list):
        try:
            encrypt.write_salt_to_file(filename[0], self.salt)
        except TypeError:
            return False

    # open keyfile if toggle on, or salt if togle off
    def open_keyfile(self):
        if self.ids.switch1.active:
            self.password = bytes(self.ids.password.text, 'utf-8')
            if self.password == bytes("", 'utf-8'):
                toast("Please enter a passphrase")
            else:
                filechooser.open_file(on_selection=self.read_salt_file)
            return self.password
        else:
            filechooser.open_file(on_selection=self.read_keyfile)

    # reads keyfile and returns fernet token, toast message if no file selected
    def read_keyfile(self, filename: list):
        try:
            if filename[0].endswith('.key'):
                self.fernet = encrypt.read_keyfile(filename[0])
                filechooser.open_file(on_selection=self.encrypt_file)
                return self.fernet
            else:
                toast("Please select a keyfile")
        except TypeError:
            return False

    # reads salt from file with extension .key
    def read_salt_file(self, filename: list):
        try:
            if filename[0].endswith('.key'):
                self.salt = encrypt.read_salt_file(filename[0])
                self.key = encrypt.generate_key_from_salt(self.password, self.salt)
                self.fernet = encrypt.generate_fernet(self.key)
                filechooser.open_file(on_selection=self.encrypt_file)
                print(f'fernet type', {self.fernet}, self.fernet)
                print(f"Salt: {self.salt}")
                return self.fernet
            else:
                toast("Please select a keyfile")
        except TypeError:
            return False

    # encrypt the file using the fernet returned from read_<key/salt>_file()
    def encrypt_file(self, file_to_encrypt: list):
        encrypt.encrypt_file(file_to_encrypt[0], self.fernet)
        toast("Success!")


# decryption screen
class DecryptScreen(Screen):

    def __init__(self, **kwargs):
        super(DecryptScreen, self).__init__(**kwargs)
        self.salt = None
        self.password = None
        self.key = None
        self.fernet = None

    # called when pressing button, reads keyfile or salt based on switch toggle
    # returns password in bytes if using with password
    def open_keyfile(self):
        if self.ids.switch2.active:
            self.password = bytes(self.ids.password.text, 'utf-8')
            print(self.password)
            if self.password == bytes("", 'utf-8'):
                toast("Please enter a passphrase")
            else:
                filechooser.open_file(on_selection=self.read_salt_file)
                print(f"Read from salt file, password is: {self.password}")
                return self.password
        else:
            filechooser.open_file(on_selection=self.read_keyfile)

    # reads keyfile and returns fernet token, toast message if no file selected
    def read_keyfile(self, filename: list):
        try:
            if filename[0].endswith('.key'):
                self.fernet = encrypt.read_keyfile(filename[0])
                filechooser.open_file(on_selection=self.decrypt_file)
                print(f'fernet type', {self.fernet}, self.fernet)
                return self.fernet
            else:
                toast("Please select a keyfile")
        except TypeError:
            return False

    # reads salt from file with extension .key
    def read_salt_file(self, filename: list):
        try:
            if filename[0].endswith('.key'):
                self.salt = encrypt.read_salt_file(filename[0])
                self.key = encrypt.generate_key_from_salt(self.password, self.salt)
                self.fernet = encrypt.generate_fernet(self.key)
                filechooser.open_file(on_selection=self.decrypt_file)
                print(f'fernet type', {self.fernet}, self.fernet)
                print(f"Salt: {self.salt}")
                return self.fernet
            else:
                toast("Please select a keyfile")
        except TypeError:
            return False

    # decrypt the file using the fernet returned from read_<key/salt>_file()
    def decrypt_file(self, file_to_decrypt: list):
        try:
            encrypt.decrypt_file(file_to_decrypt[0], self.fernet)
            toast("Success!", background=[0, 128, 128, .5])
        except Exception as InvalidToken:
            print(InvalidToken)
            toast("Decryption unsuccessful!", background=[1, 0, 0, 1])


# Navigation drawer to declare screen_manager and nav_drawer properites
class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class MainApp(MDApp):

    # build the app, pass in desired theme and color
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "400"
        Builder.load_file('main.kv')


if __name__ == '__main__':
    MainApp().run()
