from django.forms import model_to_dict
from constants.error_code import ErrorCode
from savnet.log.models import FPath


def test():
    asn_path = FPath.objects.values('fp_id', 'dst_prefix', 'asn_path')
    resp_data = {
        'ASN_Path': asn_path,
    }
    return resp_data