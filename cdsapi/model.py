# yes

__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


import inspect
import logging
import wsme
import datetime
from wsme import types as wtypes


LOG = logging.getLogger(__name__)


class _Base(object):

    def __init__(self, **kwds):
        self.fields = list(kwds)
        for k, v in kwds.iteritems():
            setattr(self, k, v)

    @classmethod
    def from_model(cls, m):
        return cls(**(m.as_dict()))

    def as_dict(self):
        d = {}
        for f in self.fields:
            v = getattr(self, f)
            if isinstance(v, _Base):
                v = v.as_dict()
            elif isinstance(v, list) and v and isinstance(v[0], _Base):
                v = [sub.as_dict() for sub in v]
            d[f] = v
        return d

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    @classmethod
    def get_field_names(cls):
        fields = inspect.getargspec(cls.__init__)[0]
        return set(fields) - set(["self"])


class Driver(_Base):

    name = wtypes.text
    status = wsme.wsattr(bool, default=True)

    @classmethod
    def from_db_model(cls, m):
        return cls(
            name=m.name,
            status=m.status)


class IpTable(_Base):
    ipaddress = wtypes.text
    vlan_id = int
    is_alloc = wsme.wsattr(bool, default=False)


class Template(_Base):
    template_name = wtypes.text
    core_num = int
    ram = int
    disk = int
    extend_disk = int


class Instances(_Base):

    instance_uuid = wtypes.text
    name = wtypes.text
    ip = wtypes.text
    # across api set action in [add, delete]
    status = wtypes.text
    # across agent set action value in [None, delete, deleting]
    template_type = wtypes.text  # suporrt only two kinds of iaas, [vsphere, openstack]
    os_type = wtypes.text
    username = wtypes.text
    passwd = wtypes.text
    time = {wtypes.text: wtypes.text}  # online_time, off_time, create_time
    iaas_type = wtypes.text
    customers = wtypes.text


class Tasks(_Base):

    task_id = wtypes.text  # task id
    create_time = datetime.datetime  # create time
    template_type = wtypes.text  # Instances template type , eg: large, tiny, small
    model_type = wtypes.text
    status = wtypes.text  # task status [OK, PROCESSING, ERROR]
    instances_num = int  # in this task has instances_num instances
    completed_num = int  # in processing already completed instances number
    completed_instances = [Instances]  # already completed instances detail

    @classmethod
    def from_db_model(cls, m, completed_num, instances):
        return cls(task_id=m[0],
                   create_time=m[1],
                   template_type=m[2],
                   model_type=m[3],
                   status=m[4],
                   instances_num=m[5],
                   completed_num=completed_num,
                   completed_instances=instances)