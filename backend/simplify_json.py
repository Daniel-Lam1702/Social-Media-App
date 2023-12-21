import json

with open('world_universities_and_domains.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

universitites_dict = {}
for college in data:
    college_name = college['name']
    for domain in college['domains']:
        universitites_dict[domain] = college_name
    
with open('world_universities_and_domains_simplified.json', 'w', encoding='utf-8') as file:
    json.dump(universitites_dict, file, indent=4, ensure_ascii=False)