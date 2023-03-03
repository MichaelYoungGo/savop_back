import os
from django.forms import model_to_dict
from constants.error_code import ErrorCode
from savnet.log.models import FPath


def test():
    asn_path = FPath.objects.values('fp_id', 'dst_prefix', 'asn_path')
    resp_data = {
        'ASN_Path': asn_path,
    }
    return resp_data

class SavnetContrller:
    def start(self):
        pass
    def refresh(slef):
        pass
    @staticmethod
    def get_log_data(path="/root/savnet_bird/logs", file_name = "server.log"):
        subdirs = [os.path.join(path, o) for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))]
        info = []
        for subdir_i in subdirs:
            with open(os.path.join(subdir_i, file_name), mode="r") as f:
                lines = f.readlines()
                for line in lines:
                    if "[INFO]" not in line:
                        continue
                    info.append(line)
                    print(line)
        return "aaa"