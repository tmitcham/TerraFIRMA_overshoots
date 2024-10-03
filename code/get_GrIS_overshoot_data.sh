# RUN_IDS=( cs568 cx209 cy837 cy838 cz374 cz375 cz376 cz377 cz376 cz377 cz378 cz944 da800 da697 da892 db223 dc251 dc051 dc052 dc248 dc249 db956 dc565 dd210 dc032 dc123 dc130 )

# RUN_IDS=( cs568 cx209 cy837 cy838 cz375 cz376 cz377 dc051 dc052 df028 dc123 dc130 )

# RUN_IDS=( dc123 dc130 )

RUN_IDS=( cw988 cw989 cw990 cy623 da914 da916 da917 )

for ID in "${RUN_IDS[@]}"; do
  if [ ! -d ../raw_data/${ID} ]; then
    mkdir -p ../raw_data/${ID}
    mkdir -p ../raw_data/${ID}/atmos
    mkdir -p ../raw_data/${ID}/icesheet
  fi
  moo get -I :crum/u-${ID}/chy.file/*GrIS.hdf5 ../raw_data/${ID}/icesheet/ &
done
