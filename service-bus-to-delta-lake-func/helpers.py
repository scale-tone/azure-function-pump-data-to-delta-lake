from jsonpath_ng import parse

def apply_jsonpath(msg, json_path):
    
    results = parse(json_path).find(msg)

    if len(results) == 1:
        # jsonpath produced an object - just returning it
        return results[0].value
    else:
        # jsonpath produced an array - trying to convert it back into object
        record = {}
        for res in results:
            record[res.path.fields[0]] = res.value

        return record
