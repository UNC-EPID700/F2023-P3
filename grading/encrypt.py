from cryptography.fernet import Fernet
import os


def main():
    key = Fernet.generate_key()

    with open('p3_key.key', 'wb') as filekey:
        filekey.write(key)

    with open('p3_key.key', 'rb') as filekey:
        key = filekey.read()

    # using the generated key
    fernet = Fernet(key)

    for filename in os.listdir(os.path.join(os.getcwd(), "grading", "encrypted")):
        filen = os.path.join(os.getcwd(),
                             "grading", "encrypted", filename)
        print(filen)

        with open(filen, 'rb') as f, open(os.path.join(os.getcwd(), "grading", "encrypted", f"{filename}_encrypted"), 'wb') as encrypt_f:
            f_bytes = f.read()
            encrypted = fernet.encrypt(f_bytes)
            encrypt_f.write(encrypted)


if __name__ == "__main__":
    main()
