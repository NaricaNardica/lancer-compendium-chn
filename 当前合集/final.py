import json
import glob
import os

def process_data(obj):
    target_keys = {'flavor','tactics','trigger','tokenName', 'name', 'description', 'detail','passive_name','passive_effect','active_effect','active_name','effect','on_hit','on_attack','effects'}
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            processed_value = process_data(value)
            if key in target_keys:
                new_dict[key] = processed_value
            else:
                if is_non_empty(processed_value):
                    new_dict[key] = processed_value
        return new_dict
    elif isinstance(obj, list):
        processed_list = [process_data(item) for item in obj]
        filtered_list = [item for item in processed_list if is_non_empty(item)]

        if all(isinstance(item, dict) and 'name' in item for item in filtered_list):
            converted_dict = {}
            for item in filtered_list:
                converted_dict[item['name']] = item
            return converted_dict
        return filtered_list
    else:
        return obj


def is_non_empty(value):
    return bool(value) if isinstance(value, (dict, list)) else False


def process_and_wrap(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    processed = process_data(data)
    if isinstance(processed, dict) and 'name' in processed:
        return {processed['name']: processed}
    return {}


def batch_process(input_files, output_file):
    merged_data = {}

    for file in input_files:
        try:
            result = process_and_wrap(file)
            merged_data.update(result)
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

def transform_data(data):
    for key in data:
        item = data[key]
        # 合并system字段内容到外层
        if "system" in item:
            system_content = item["system"]
            # 更新条目内容
            item.update(system_content)
            # 删除system字段
            del item["system"]
    return data

def printJson(source,target,template):#source:文件夹名 target：文件名 template:模板

    input_files = glob.glob('./input/'+source+'/*.json')  # 获取当前目录所有json文件
    batch_process(input_files, 'output/'+target+'merged_output.json')
    with open('output/'+target+'merged_output.json', "r", encoding="utf-8") as f:
        data = json.load(f)

    transformed_data = transform_data(data)

    with open('output/'+target+'.json', "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, indent=2, ensure_ascii=False)
    #此处为模板处理
    # 读取文件1
    with open('template/'+template+'.json', 'r', encoding='utf-8') as f:
        file1_data = json.load(f)

    # 读取文件2
    with open('output/'+target+'.json', 'r', encoding='utf-8') as f:
        file2_data = json.load(f)

    # 替换entries字段
    file1_data["entries"] = file2_data

    # 输出合并后的文件
    with open('output/'+template+'.json', 'w', encoding='utf-8') as f:
        json.dump(file1_data, f,
                  indent=2,
                  ensure_ascii=False,  # 保持非ASCII字符原样输出
                  separators=(',', ': '))  # 保持美观的冒号间距

    # 此处模板处理结束

    os.remove('output/'+target+'merged_output.json')
    os.remove('output/' + target + '.json')




# 使用示例：处理当前目录所有json文件
if __name__ == "__main__":
    printJson('input_mech_item', 'mech_item','world.mech-items')
    printJson('input_npc_item', 'npc-item','world.npc-items')
    printJson('input_npc-actors', 'npc-actor', 'world.npc-actors')
    printJson('input_pilot_items', 'pilot_items', 'world.pilot-items')
    printJson('input_player_actors', 'player_actors', 'world.player-actors')
    printJson('input_status', 'status', 'world.status-items')



