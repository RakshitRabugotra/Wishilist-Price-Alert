# Amazon Wishlist
## Development
Add a python virtual environment to the root directory same level as `app.py`. 
```console
$ python -m venv venv
```
Active the script:

  + For `git bash` | `macOS`
    ```console
    $ source ./venv/Scripts/activate
    ```

  + For `windows`, run `powershell` as administrator
    ```console
    > Set-ExecutionPolicy RemoteSigned
    > .\venv\Scripts\Activate.ps1
    > Set-ExecutionPolicy Restricted
    ```

### Install all the python-dependencies

```console
$ python -m pip install -r requirements.txt --upgrade
```

## Run the script
```console
$ python app.py
```