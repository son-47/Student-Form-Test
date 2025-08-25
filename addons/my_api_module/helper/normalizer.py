import logging
_logger = logging.getLogger(__name__)
class Normalizer():
    def __init__(self):
        pass
    

    @staticmethod
    def getColumnFromAlias(columnlist, ModelAlias2Fields):
        if not columnlist:
            return None, [item.value for item in ModelAlias2Fields] 
        if isinstance(columnlist, str):
            columnlist = columnlist.strip()
            if not columnlist:
                return None, [item.value for item in ModelAlias2Fields] 
            columnlist = columnlist.split(",")

        result = []

        for item in columnlist:
            # __members__ is a dictionary of the enum members
            if not item in ModelAlias2Fields.__members__:
                return "Danh sach cot khong hop le", None
            else:
                result.append(ModelAlias2Fields[item].value)
        return None, result
    
    @staticmethod
    def getOrderString(order, ModelAlias2Fields):
        result = []
        if not order or order.strip() == "":
            return None, "id asc"

        order_param = order.strip().split("-")
        for part in order_param:
            if ":" not in part:
                return "Cú pháp order không hợp lệ. Thiếu dấu ':'", None

            alias, direction = part.split(":")
            errMessage, field = Normalizer.getColumnFromAlias(alias.strip(), ModelAlias2Fields)
            if errMessage:
                return f"Alias không hợp lệ: {alias}", None

            direction = 'desc' if direction.strip() == '1' else 'asc'
            result.append(f"{field} {direction}")

        return None, ", ".join(result)
                
    @staticmethod
    def getModelFromJsonData(data, fieldList):
        def helper(item, fieldList):
            for field, value in item.items():
                if field not in fieldList:
                    return "Danh sách cột không hợp lệ", None
                item[field] = str(value).strip()
            return None, item

        cleaned_data = []
        for item in list(data):
            err, valid_item = helper(item, fieldList)
            if err:
                return err, None
            cleaned_data.append(valid_item)

        return None, cleaned_data
    
    
    @staticmethod
    def getModelDataFromLabels(data, modelFields2Labels):
        def helper(item, labels2Fields):
            res = {}
            for field, value in item.items():
                if field not in labels2Fields.keys():
                    _logger.error(f"Cột '{field}' trong file KHÔNG khớp với labels2Fields: {list(labels2Fields.keys())}")
                    return "Danh sach cot khong hop le", None
                res[labels2Fields[field]] = value
            return None, res
        
        labelList = [e.value for e in modelFields2Labels]
        fieldList = [e.name for e in modelFields2Labels]
        labels2Fields = dict(zip(labelList, fieldList))
        _logger.info(f"Field trả về là :{labels2Fields}")
        cleaned_data = []
        for item in list(data):
            err, valid_item = helper(item, labels2Fields)
            if err:
                return err, None
            cleaned_data.append(valid_item)

        return None, cleaned_data