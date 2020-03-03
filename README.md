# prometheus_dorado_exporter
Prometheus exporter for Huawei Dorado SAN

## Running

1. Specify your Dorado superadmin credentials inside `dorado_exporter/config.ini`. Admin is not able to collect metrics. So superadmin creds is the only option
2. Run `docker-compose build && docker-compose up`
3. Configure prometheus to collect data from *your_exporter_ip:9720*. Note: you must pass your SAN address with "address" GET parameter (http://your_exporter_ip:9720?address=your_dorado_ip:port)
