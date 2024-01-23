FROM prom/prometheus
RUN mkdir /tmp/file_base
CMD ["--config.file=/etc/prometheus/prometheus.yml", "--web.external-url=/prometheus/"]
ENTRYPOINT ["/bin/prometheus2"]
