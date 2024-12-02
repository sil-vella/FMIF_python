Updating data (images/facts/database)

run /Users/sil/Documents/Work/00Utilities/scripts/py/imgsearch_facedetect_savetoproj
This will take celebs from the /Users/sil/Documents/Work/reignofplay/FMIF/app_dev/FMIF_python/celebs_data/celeb_names_to_add.json,
seraches for their images and processes them.

Then run /Users/sil/Documents/Work/00Utilities/scripts/py/update_fmif_server/run.py
This will copy the new images from celebs_data to the server, if not already present and replaces the non img files. (like celeb_data.json)
It will then run populate_db.py on the server to add the new celebs to the db.

If you need to remove images from celebs_data on local after already uploading them to server, run /Users/sil/Documents/Work/00Utilities/scripts/py/update_fmif_server/run_remove.py,
This will find images on the server that are not in the local images dir, and deletes them.