import logging
from django.db import models

logger = logging.getLogger(__name__)

class FPath(models.Model):
    '''
    Table: forwardingpath_tab
    '''
    fp_id = models.CharField(max_length=50)
    dst_prefix = models.CharField(max_length=50)
    asn_path = models.TextField()
    c_time = models.DateTimeField(auto_now_add=True, blank=True) # time of creating a table entry
    m_time = models.DateTimeField(auto_now=True, blank=True) # time of modifying a table entry

    class Meta:
        db_table = 'forwardingpath_tab'

class SAVTab(models.Model):
    '''
    Table: sav_tab
    '''
    sav_tab_id = models.CharField(max_length=50)
    src_prefix = models.CharField(max_length=50)
    in_interface = models.CharField(max_length=1024) # incoming interface
    mask = models.CharField(max_length=1024)
    router_id = models.CharField(max_length=50)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'sav_tab'

class MsgTab(models.Model):
    '''
    Table: message_tab
    '''
    msg_id = models.CharField(max_length=50)
    msg_name = models.CharField(max_length=1024)
    src_router = models.CharField(max_length=50)
    dst_router = models.CharField(max_length=50)
    origin_as = models.CharField(max_length=1024)
    prop_scope = models.CharField(max_length=1024)
    msg_path = models.TextField()
    timestamp = models.CharField(max_length=1024)
    prefix_id = models.CharField(max_length=50)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'msg_tab'

class RouterTab(models.Model):
    '''
    Table: router_tab
    '''
    router_id = models.CharField(max_length=50)
    router_no = models.CharField(max_length=1024)
    router_name = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'router_tab'

class LinkTab(models.Model):
    '''
    Table: link_tab
    '''
    link_id = models.CharField(max_length=50)
    src_router = models.CharField(max_length=50)
    dst_router = models.CharField(max_length=50)
    src_router_interface = models.CharField(max_length=1024)
    dst_router_interface = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'link_tab'

class PrefixTab(models.Model):
    '''
    Table: prefix_tab
    '''
    prefix_id = models.CharField(max_length=50)
    prefix_name = models.CharField(max_length=1024)
    mask = models.CharField(max_length=1024)
    router_id = models.CharField(max_length=50)
    sav_tab_id = models.CharField(max_length=50)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'prefix_tab'

class InterfaceTab(models.Model):
    '''
    Table: interface_tab
    '''
    interface_id = models.CharField(max_length=50)
    interface_name = models.CharField(max_length=1024)
    router_id = models.CharField(max_length=50)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'interface_tab'

class LogTab(models.Model):
    '''
    Table: log_tab
    '''
    log_id = models.CharField(max_length=50)
    dst_prefix = models.CharField(max_length=50)
    dst_mask = models.CharField(max_length=1024)
    asn_path = models.TextField()
    src_prefix = models.CharField(max_length=50)
    src_mask = models.CharField(max_length=1024)
    in_interface = models.CharField(max_length=1024)
    router_id = models.CharField(max_length=50)
    msg_name = models.CharField(max_length=1024)
    src_router = models.CharField(max_length=50)
    dst_router = models.CharField(max_length=50)
    origin_as = models.CharField(max_length=1024)
    prop_scope = models.CharField(max_length=1024)
    msg_path = models.TextField()
    timestamp = models.CharField(max_length=1024)
    prefix_id = models.CharField(max_length=50)
    router_no = models.CharField(max_length=1024)
    router_name = models.CharField(max_length=1024)
    src_router_interface = models.CharField(max_length=1024)
    dst_router_interface = models.CharField(max_length=1024)
    prefix_name = models.CharField(max_length=1024)
    sav_tab_id = models.CharField(max_length=50)
    interface_name = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    m_time = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = 'log_tab'