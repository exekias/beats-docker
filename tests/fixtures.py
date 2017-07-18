import os
import pytest

try:
    version = os.environ['ELASTIC_VERSION']
except KeyError:
    version = open('version.txt').read().strip()


class Beat:
    def __init__(self, name, process, home_dir, data_dir, config_dir, log_dir,
                 kibana_dir, binary_file, config_file, capabilities, version_tag):
        self.name = name
        self.process = process
        self.home_dir = home_dir
        self.data_dir = data_dir
        self.config_dir = config_dir
        self.log_dir = log_dir
        self.kibana_dir = kibana_dir
        self.binary_file = binary_file
        self.config_file = config_file
        self.version = version
        self.capabilities = capabilities
        self.version_tag = version_tag


@pytest.fixture()
def beat(Process, File, TestinfraBackend, Command):
    # We name the container after the Beat, so asking for the hostname
    # lets us know which Beat we are testing.
    beat_name = TestinfraBackend.get_hostname()
    beat_home = os.path.join(os.sep, 'usr', 'share', beat_name)
    binary_file = File(os.path.join(beat_home, beat_name))

    capability_string = Command.check_output('getcap %s' % binary_file.path)
    # Like: '/usr/share/packetbeat/packetbeat = cap_net_admin,cap_net_raw+eip'
    if capability_string:
        capabilities = capability_string.split()[-1].split('+')[0].split(',')
        # Like: ['cap_net_raw', 'cap_net_admin']
    else:
        capabilities = []

    return Beat(
        name=beat_name,
        process=Process.get(comm=beat_name),
        home_dir=File(beat_home),
        data_dir=File(os.path.join(beat_home, 'data')),
        config_dir=File(beat_home),
        log_dir=File(os.path.join(beat_home, 'logs')),
        kibana_dir=File(os.path.join(beat_home, 'kibana')),
        config_file=File(os.path.join(beat_home, '%s.yml' % beat_name)),
        binary_file=binary_file,
        capabilities=capabilities,
        version_tag=os.environ.get('VERSION_TAG', version),
    )
