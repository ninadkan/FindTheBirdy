REM use to create key.json
REM set the environment variable GOOGLE_APPLICATION_CREDENTIALS=key.json
gcloud iam service-accounts keys create key.json --iam-account vision-quickstart@findthebird-ninadk.iam.gserviceaccount.com
set GOOGLE_APPLICATION_CREDENTIALS=key.json
