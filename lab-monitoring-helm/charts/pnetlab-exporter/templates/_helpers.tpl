{{- define "joinList" }}
{{- $arr := .arr }}
{{- $list := list }}
{{- range $arr }}
{{- $list = append $list .host }}
{{- end }}
{{- join "," $list }}
{{- end }}
