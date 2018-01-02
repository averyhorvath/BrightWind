counter=0
for FILE in $(ls)
do
  sleep 1
  if [ $FILE != 'copy.sh' ]; then
  START_TIME=$SECONDS
  let counter++
  cqlsh -e "COPY merra_two.reanalysis (locationid, readingdtm, u50m, v50m, t2m, ps) FROM '$FILE';"
  if [ $? -eq 0 ]; then
    echo echo "$counter: $FILE"
    mv ./$FILE ../processed/$FILE
  else
    sleep 5
    echo FIRST COPY FAILED
    cqlsh -e "COPY merra_two.reanalysis (locationid, readingdtm, u50m, v50m, t2m, ps) FROM '$FILE';"
    if [ $? -eq 0 ]; then
      echo echo "$counter: $FILE"
      mv ./$FILE ../processed/$FILE
    else
      echo COPY FAILED
      exit 1
    fi  
  fi
  ELAPSED_TIME=$(($SECONDS - $START_TIME))
  fi
done