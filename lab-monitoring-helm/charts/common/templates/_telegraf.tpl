{{- define "common.telegraf.influxdbConfig" -}}
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "sDQUzg2yzNmiRNXppIr0"
  organization = "SVTech"
  bucket = "telegraf"
{{- end -}}

{{- define "common.telegraf.kafkaConfig" -}}
[[outputs.kafka]]
  brokers = ["kafka-kafka-brokers:9092"]
  topic = "telegraf"
{{- end -}}
