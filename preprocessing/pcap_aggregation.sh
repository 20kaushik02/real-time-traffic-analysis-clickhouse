#!/bin/bash

data_year=2023
data_month=10

# some info

total_size=0
for data_day in {01..31}; do
	pcap_size=$(curl -sI "http://mawi.nezu.wide.ad.jp/mawi/samplepoint-F/${data_year}/${data_year}${data_month}${i}1400.pcap.gz" |
		grep Content-Length |
		awk '{printf "%.3f", $2/1024/1024/1024}')
	echo "${data_year}-${data_month}-${data_day} - ${pcap_size} GB"
	total_size=$(echo $total_size + $pcap_size | bc -l)
done

echo "Total size (compressed) of ${data_year}-${data_month} - ${total_size} GB"
# Total size (compressed) of 2023-10 - 193.292 GB

# extracting data

mkdir -p csv_files

for data_day in {01..31}; do
	if [[ ! -f "${data_year}${data_month}${data_day}1400.pcap.gz" ]]; then
		wget "http://mawi.nezu.wide.ad.jp/mawi/samplepoint-F/${data_year}/${data_year}${data_month}${data_day}1400.pcap.gz"
	fi
	gzip -d "${data_year}${data_month}${data_day}1400.pcap.gz"

	# 10000 packets from each day
	python3 pcap_processor.py \
		--pcap_file "${data_year}${data_month}${data_day}1400.pcap" \
		--out_file csv_files/${data_day}.csv \
		--sample \
		--stream_size 10000

	rm "${data_year}${data_month}${data_day}1400.pcap"
done

# merge all CSV together
awk '(NR == 1) || (FNR > 1)' csv_files/*.csv > csv_files/merged.csv
