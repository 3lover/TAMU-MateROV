# ArduSub SITL (Software-In-The-Loop) for Team Oceanus GNC
# Builds the real ArduSub firmware so the simulated vehicle behaves exactly
# like the Navigator + BlueOS stack will on hardware.
#
# Build takes ~20-40 min and ~3 GB the first time (one-time cost, cached after).
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
# Which ArduSub release to build. Override with:
#   docker compose build --build-arg ARDUSUB_REF=Sub-4.5
ARG ARDUSUB_REF=Sub-4.5

RUN apt-get update && apt-get install -y --no-install-recommends \
        git sudo lsb-release tzdata ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --depth 1 -b ${ARDUSUB_REF} https://github.com/ArduPilot/ardupilot.git
WORKDIR /opt/ardupilot
RUN git submodule update --init --recursive --depth 1

# ArduPilot's own prereq installer (pulls MAVProxy, empy, build deps, etc.)
RUN USER=root Tools/environment_install/install-prereqs-ubuntu.sh -y

# Configure + build the ArduSub SITL binary
RUN . /root/.profile && ./waf configure --board sitl && ./waf sub

ENV PATH="/opt/ardupilot/Tools/autotest:/root/.local/bin:${PATH}"

COPY sim_entry.sh /sim_entry.sh
RUN chmod +x /sim_entry.sh

#  5762 -> pymavlink / GNC scripts      5763 -> QGroundControl
EXPOSE 5762 5763
ENTRYPOINT ["/sim_entry.sh"]
