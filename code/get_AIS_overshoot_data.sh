# (cs495) cs568 cx209 cw988 cw989 cw990 (cz826)
# cy837 cy838 cz374 cz375 cz376 cz377 cz378 
# cz834 cz855 cz859 db587 db723 db731
# da087 da266 db597 db733 dc324
# cz944 di335 da800 da697 da892 db223 df453 de620 dc251 db956
# dc051 dc052 dc248 dc249 dc565 dd210 dc032 df028 de621 dc123 dc130
# df025 df027 df021 df023 dh541 dh859
# de943 de962 de963 dk554 dk555 dk556

RUN_IDS=( cs568 cx209 cw988 cw989 cw990 cy837 cy838 cz374 cz375 cz376 cz377 cz378 cz834 cz855 cz859 db587 db723 db731 da087 da266 db597 db733 dc324 cz944 di335 da800 da697 da892 db223 df453 de620 dc251 db956 dc051 dc052 dc248 dc249 dc565 dd210 dc032 df028 de621 dc123 dc130 df025 df027 df021 df023 dh541 dh859 de943 de962 de963 dk554 dk555 dk556 cs495 cz826 )

for ID in "${RUN_IDS[@]}"; do
  if [ ! -d ../raw_data/${ID} ]; then
    mkdir -p ../raw_data/${ID}
    mkdir -p ../raw_data/${ID}/atmos
    mkdir -p ../raw_data/${ID}/icesheet
  fi
  moo get -ig :crum/u-${ID}/chy.file/*AIS.hdf5 ../raw_data/${ID}/icesheet/
  moo select -i surfaceT.query :crum/u-${ID}/apz.pp ../raw_data/${ID}/atmos/
done