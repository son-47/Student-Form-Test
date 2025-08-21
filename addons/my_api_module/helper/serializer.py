from datetime import datetime,date
import logging
_logger = logging.getLogger(__name__)
class Serializer():
    def __init__(self):
        pass
    
    @staticmethod
    def decode_bitmask_to_hobbies_string(bitmask):
            bits = [(bitmask >> i) & 1 for i in range(29)]
            return ','.join(str(b) for b in bits)
    # ##decode hobbies về chuỗi 0,1,...
    
    @staticmethod
    def serialize_1_item(item, columnlist, modelFields2Labels=None):
            # _logger.info(f"DEBUG - item type: {type(item)}")
            # _logger.info(f"DEBUG - item._fields: {item._fields}")
            
            # Lấy ra tất cả các field của 1 bản ghi, trả về một list các tuple
            field_value_pairs = [(field, getattr(item, field)) for field in item._fields]    
            res = {}
            for field, value in field_value_pairs:
                if field in columnlist:
                    # if endUser:
                    #     field = modelFields2Labels[field].value
                    # truy cập vào khóa ngoại của Student thì chỉ lấy id 
                    if hasattr(value, 'id'):
                        res[field] = getattr(value, 'id')
                    elif isinstance(value, (datetime,date)):
                        res[field] = value.strftime("%Y-%m-%d")
                    elif field == 'hobbies':
                        res[field] = Serializer.decode_bitmask_to_hobbies_string(value)
                    elif value in [None, False]:
                        res[field] = ""
                    elif field == 'password':
                        res[field] = "********"
                    else:
                        res[field] = value
                        
            if 'id' in res:
                id_value = res.pop('id')
                res = {'id': id_value, **res}
            # _logger.info(f"DEBUG - Final result keys: {list(res.keys())}")
            return res
    
    @staticmethod
    def serialize(data, columnlist, modelFields2Labels):
        # def decode_bitmask_to_hobbies_string(bitmask):
        #     bits = [(bitmask >> i) & 1 for i in range(29)]
        #     return ','.join(str(b) for b in bits)
        # def serialize_1_item(item, columnlist, modelFields2Labels=None):
        #     _logger.info(f"DEBUG - item type: {type(item)}")
        #     _logger.info(f"DEBUG - item._fields: {item._fields}")
            
        #     # Lấy ra tất cả các field của 1 bản ghi, trả về một list các tuple
        #     field_value_pairs = [(field, getattr(item, field)) for field in item._fields]    
        #     res = {}
        #     for field, value in field_value_pairs:
        #         if field in columnlist:
        #             # if endUser:
        #             #     field = modelFields2Labels[field].value
        #             # truy cập vào khóa ngoại của Student thì chỉ lấy id 
        #             if hasattr(value, 'id'):
        #                 res[field] = getattr(value, 'id')
        #             elif isinstance(value, (datetime,date)):
        #                 res[field] = value.strftime("%Y-%m-%d")
        #             elif field == 'hobbies':
        #                 res[field] = decode_bitmask_to_hobbies_string(value)
        #             elif value in [None, False]:
        #                 res[field] = ""
        #             else:
        #                 res[field] = value
                        
        #     if 'id' in res:
        #         id_value = res.pop('id')
        #         res = {'id': id_value, **res}
        #     _logger.info(f"DEBUG - Final result keys: {list(res.keys())}")
        #     return res
            

        if isinstance(data, list):
            return [Serializer.serialize_1_item(item, columnlist, modelFields2Labels) for item in data]
        return [Serializer.serialize_1_item(data, columnlist, modelFields2Labels)]