{{/*
Common labels applied to every resource.
*/}}
{{- define "microtask.labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels — used in matchLabels and Service selectors.
Must be stable (never change after first deploy).
*/}}
{{- define "microtask.selectorLabels" -}}
app.kubernetes.io/name: {{ .name }}
app.kubernetes.io/instance: {{ .release }}
{{- end }}

{{/*
Build a fully-qualified image string: repository:tag
Usage: {{ include "microtask.image" .Values.api.image }}
*/}}
{{- define "microtask.image" -}}
{{- printf "%s:%s" .repository .tag -}}
{{- end }}

{{/*
Database host: returns the in-cluster Service name when MySQL is enabled (dev),
or the external RDS endpoint when MySQL is disabled (prod).
Usage: {{ include "microtask.dbHost" . }}
*/}}
{{- define "microtask.dbHost" -}}
{{- if .Values.mysql.enabled -}}
mysql
{{- else -}}
{{ .Values.db.host }}
{{- end -}}
{{- end }}
