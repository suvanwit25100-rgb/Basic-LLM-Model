import json

input_file = "physics_tutor_dataset.jsonl"
output_file = "mlx_training_data.jsonl"

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        data = json.loads(line)
        
        instruction = data.get("instruction", "")
        response = data.get("response", "")
        
        formatted_text = f"<s>[INST] {instruction} [/INST] {response} </s>"
        
        new_json_line = {"text": formatted_text}
        
        json.dump(new_json_line, outfile, ensure_ascii=False)
        outfile.write('\n')

print(f"✅ Formatting complete! Created {output_file}")