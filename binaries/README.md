Warning: binary versions are not actively updated, and this is not actively maintained. This is a one off snapshot of [version 0.13](https://pypi.org/project/mysocketctl/0.13/)


To download:
```
wget https://github.com/mysocketio/mysocketctl/raw/main/binaries/mysocketctl
chmod +x ./mysocketctl
```


Linux binary for mysocketctl was created using pyinstaller:

```pyinstaller --onefile --additional-hooks-dir=. -w /usr/local/bin/mysocketctl```
