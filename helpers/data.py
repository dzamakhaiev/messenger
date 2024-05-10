import copy


def corrupt_json_field(json_dict: dict, incorrect_field: str, value='incorrect'):
    incorrect_dict = copy.copy(json_dict)

    if 'and' not in incorrect_field:
        incorrect_dict[incorrect_field] = value

    else:
        fields = incorrect_field.split('and')
        fields = [field.strip() for field in fields]
        for field in fields:
            incorrect_dict[field] = value

    return incorrect_dict


def remove_json_field(json_dict: dict, remove_field: str):
    incorrect_dict = copy.copy(json_dict)

    if 'and' not in remove_field:
        incorrect_dict.pop(remove_field)

    else:
        fields = remove_field.split('and')
        fields = [field.strip() for field in fields]
        for field in fields:
            incorrect_dict.pop(field)

    return incorrect_dict
