# yes

__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


import inspect
import logging
import wsme
import ast
import six
import datetime
from wsme import types as wtypes


LOG = logging.getLogger(__name__)
operation_kind = wtypes.Enum(str, 'lt', 'le', 'eq', 'ne', 'ge', 'gt')


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


class Query(_Base):
    """Query filter."""

    # The data types supported by the query.
    _supported_types = ['integer', 'float', 'string']

    # Functions to convert the data field to the correct type.
    _type_converters = {'integer': int,
                        'float': float,
                        'string': six.text_type}

    _op = None  # provide a default

    def get_op(self):
        return self._op or 'eq'

    def set_op(self, value):
        self._op = value

    field = wtypes.text
    "The name of the field to test"

    # op = wsme.wsattr(operation_kind, default='eq')
    # this ^ doesn't seem to work.
    op = wsme.wsproperty(operation_kind, get_op, set_op)
    "The comparison operator. Defaults to 'eq'."

    value = wtypes.text
    "The value to compare against the stored data"

    type = wtypes.text
    "The data type of value to compare against the stored data"

    def __repr__(self):
        # for logging calls
        return '<Query %r %s %r %s>' % (self.field,
                                        self.op,
                                        self.value,
                                        self.type)

    def as_dict(self):
        return self.as_dict_from_keys(['field', 'op', 'type', 'value'])


class TaskUuid(_Base):
    task_id = wtypes.text

    @classmethod
    def from_model(cls, task_id):
        return cls(task_id=task_id)


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


class InstancesType(_Base):
    name = wtypes.text
    core_num = int
    ram = int
    disk = int
    extend_disk = int


class TemplateType(_Base):
    iaas_type = wtypes.text
    image_type = wtypes.text


class Instances(_Base):

    instance_uuid = wtypes.text
    name = wtypes.text
    hostname = wtypes.text
    ip = wtypes.text
    # across api set action in [add, delete]
    status = wtypes.text
    # across agent set action value in [None, delete, deleting]
    os_type = wtypes.text
    template_type = wtypes.text  # suporrt image  eg:[ubuntu, centos...]
    model_type = wtypes.text  # InstancesType
    username = wtypes.text
    passwd = wtypes.text
    # time = {wtypes.text: wtypes.text}  # online_time, off_time, create_time
    iaas_type = wtypes.text
    customers = wtypes.text
    # options = {wtypes.text: wtypes.text}

    @classmethod
    def from_db_model(cls, m):
        l = []
        vsphere_instance_name = m[2]
        if vsphere_instance_name:
            name = vsphere_instance_name.split('-', 6)
            l.append(name[0])
            l.append(name[6])
            instance_name = '-'.join(l)

        return cls(instance_uuid=m[0],
                   name=vsphere_instance_name,
                   hostname=instance_name,
                   ip=m[3],
                   status=m[4],
                   os_type=m[5],
                   username=m[6],
                   passwd=m[7],
                   template_type=m[8],
                   instance_type=m[9],
                   iaas_type=m[10],
                   customers=m[11])


class Tasks(TaskUuid):

    # task_id = wtypes.text  # task id
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
                   instances_num=m[6],
                   completed_num=completed_num,
                   completed_instances=instances)
