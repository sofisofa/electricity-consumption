FROM grafana/grafana:latest

ARG GF_DATASRC_UID=${GF_DATASRC_UID}
ARG EN_TABLE_NAME=${EN_TABLE_NAME}

ADD ./grafana/provisioning /etc/grafana/provisioning
ADD ./grafana/dashboards /var/lib/grafana/dashboards

RUN cp /var/lib/grafana/dashboards/Electricity_Consumption_GrafanaDashboard_notexp.json /tmp
RUN sed -i "s/{GF_DATASRC_UID}/${GF_DATASRC_UID}/g" /tmp/Electricity_Consumption_GrafanaDashboard_notexp.json
RUN sed -i "s/{EN_TABLE_NAME}/${EN_TABLE_NAME}/g" /tmp/Electricity_Consumption_GrafanaDashboard_notexp.json
RUN cat /tmp/Electricity_Consumption_GrafanaDashboard_notexp.json > /var/lib/grafana/dashboards/Electricity_Consumption_GrafanaDashboard_notexp.json
RUN rm /tmp/Electricity_Consumption_GrafanaDashboard_notexp.json