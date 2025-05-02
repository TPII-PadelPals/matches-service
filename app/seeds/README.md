# Seeds
Seeds are created in Python files which offer flexibility to changes in the code and IDE typing.

## Creating new seed files
To create new seeds, use `seed_records_1.py` as example.

## Setting up a seed file
To configure a seed file, set the constant `RECORDS` of `seed_config.py` as the constant `RECORDS` of the desirable seed file.

## Running a seed file

### Manually:
```
docker exec <service containername> python <path to seed_db.py>
```

### Automaticall:

Linux:
```
./scripts/seed.sh
```

Windows:
````
./scripts/seed.bat
```
