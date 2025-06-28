from django.shortcuts import render # type: ignore
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
# Create your views here.

from .models import Chat, NameGenerator

from ollama import chat as response_generator
import json

import ast
import re
import javalang # type: ignore
import esprima #type: ignore

# for handling request raised
@csrf_exempt
def handle_request(request):
    if request.method == "POST":
        return handle_post(request)
    
    return handle_get(request)

# handling POST request (resolving of query)
def handle_post(request):
    data = json.loads(request.body)
    # code = data.get('code')
    query = data.get('query')
    chat_id = data.get('chat_id')
    # print(data)
    # print(list(Chat.objects.all()))
    return StreamingHttpResponse(processRequest(query, chat_id))

#for processing the request by bot
def processRequest(question : str, chat_id: int):
    previous_reply = str()
    previous_query = str()
    code = str()
    chat = None
    # print("Process Request" + name)
    try: 
        chat = Chat.objects.get(id=chat_id)
        # try:
        #     previous_query = chat.messages.last().query
        #     previous_reply = chat.messages.last().reply
        # except Exception as e:
        #     print(e)
    except Exception as e:
        # print(e)
        chat = Chat.objects.create(name = "New Chat")

    if chat.code:
        code = chat.code

    instruction = "Analyze the code if code is provided and answer the question."
    prompt = f"### Instruction:\n{instruction}\n\n"
    if code:
        prompt += f"### Code:\n{code}\n\n"
    if question:
        prompt += f"### Question:\n{question}\n"

    models = [
        'deepseek-coder:6.7b-instruct', # [0] 2+ mins approx
        'deepseek-coder:1.3b-instruct', # [1] 15 secs approx
        'starcoder2',                   # [2] not defined
        'starcoder2:7b',                # [3] 1+ mins approx
        'codellama:7b-instruct',        # [4] 2+ mins approx
        'mistral:7b-instruct',          # [5] 1+ mins approx
        'codegemma:instruct'            # [6] 1+ mins approx
    ]

    response = response_generator(
        model = models[6],
        messages=[
            {"role": "system", "content": "You are a coding assistant that helps with writing, debugging, and explaining code."},
            # {"role": "user", "content": previous_query},
            # {"role": "assistant", "content": previous_reply},
            {"role": "user", "content": prompt}
        ],
        stream = True
    )

    bot_reply = ""

    for chunk in response:
        out = chunk.message.content
        bot_reply += out
        yield(out)
    
    # print(name)
    message_append(chat, question, bot_reply)

#Append the current question and reply to the chat in model
def message_append(chat, question, bot_reply):
    # print(type(chat))
    chat.add_message(question, bot_reply)
    # print(chat.messages.last().reply)  


# handling GET request
def handle_get(request):
    chat_id = request.GET.get('chat_id')
    if chat_id:    
        return user_chat(chat_id)
    
    # print("Yes")
    return html_response(request)

# for user chat retrival
def user_chat(chat_id):
    chat = Chat.objects.get(id=chat_id)
    code, tree, convo = chat.get_messages()

    messages = [message.get_qanda() for message in convo]

    response = {
        'code' : code,
        'tree' : tree,
        'messages' : messages        
    }

    return JsonResponse(response)

# initial HTML page rendering
def html_response(request):
    # chats = Chat.objects.order_by("time").reverse()
    chats = Chat.objects.order_by("time")
    n = len(chats)
    
    if n > 0:
        # chat_identity = [(chat.name,chat.time) for chat in chats]
        chat_identity = [{"name" : chat.name,"id" : chat.id} for chat in chats]
    else:
        chat_identity = list()

    context = {
        'chats' : json.dumps(chat_identity),
    } 
    # print(chat_identity)
    return render(request, 'chat_page.html', context=context)

# For generating unique names
# def generate_unique(request):
#     generator = None

#     try:
#         generator = NameGenerator.objects.all()[0]
#     except:
#         generator = NameGenerator.objects.create(generator=0)

#     new_chat_name = generator.generate()
#     return HttpResponse(new_chat_name)

#Experiments
def generate_unique(request):
    name = request.GET.get("name")
    chat_name = "New Chat"
    if name.strip():
        chat_name = name
    new_chat = Chat.objects.create(name = chat_name)
    chat_id = new_chat.id
    dict = {
        "name" : chat_name,
        "id"   : chat_id 
    }
    # print("created here")
    return JsonResponse(dict)
        
# for deleting specified chats
def delete_chat(request):
    id = request.GET.get('chat_id')
    try:
        Chat.objects.get(id=id).delete()
    except:
        pass
    finally:
        return HttpResponse("Deletion Successful")
    
# For deleting the generator object to start fresh
def delete_database(request):
    try:
        NameGenerator.objects.all().delete()
        Chat.objects.all().delete()
        return HttpResponse("Deletion Successful")
    except:
        return HttpResponse("Some Error")
    
# For Updating names via change_name url
@csrf_exempt
def update_name(request):
    data = json.loads(request.body)
    new_name = data.get('new_name')
    chat_id = data.get('chat_id')
    chat = None
    try:
        chat = Chat.objects.get(id=chat_id)
        chat.name = new_name
        chat.save()
    except Exception as e:
        print(e)

    return HttpResponse("Done")
    
### EXPERIMENTING ###
# Creating a Parser for visualization

# Detect language and generate AST in tree format.
@csrf_exempt
def visualize_code(request):
    if request.method == "GET":
        return HttpResponse("It is a GET request.\nNo function to be performed")
    
    body = json.loads(request.body)
    chat_id = body.get("chat_id")
    code = body.get("code")
    # print(name)
    chat = None
    try: 
        chat = Chat.objects.get(id=chat_id)
    except Exception as e:
        # print(e)
        chat = Chat.objects.create(name="New Chat")
    
    language , ast_nodes = detect_language(code)

    tree_lines = build_tree(ast_nodes)
    tree = "Module\n" if language == "python" else "Program\n"
    for line in tree_lines[1:]:
        tree += line+"\n"

    chat.update(code,tree)

    return HttpResponse(tree)

# Detects language based on keywords (basic detection).
def detect_language(code: str) -> str:
    if "#include" in code:
        return ("cpp", parse_cpp(code))  
    if "public static void main" in code or ("class" in code and "{" in code):
        return ("java", parse_java(code))
    if ("function" in code and "{" in code) or "console.log" in code:
        return ("javascript", parse_js(code))
    
    return ("python", parse_python(code))

# Crude C/C++ parsing without libclang, works for both C and C++.
def parse_cpp(code):
    lines = code.splitlines()
    nodes = []
    current_node = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "#include" in line:
            include = re.search(r"#include\s*[<\"](.+)[>\"]", line)
            nodes.append({"label": f"Include ({include.group(1) if include else line})", "children": []})
        
        elif re.match(r"(int|void|float|double|char)\s+\w+\s*\([^)]*\)\s*{?", line):
            name = re.search(r"(int|void|float|double|char)\s+(\w+)\s*\(", line).group(2)
            current_node = {"label": f"Function ({name})", "children": []}
            nodes.append(current_node)
       
        elif re.match(r"(class|struct)\s+\w+\s*{?", line):
            name = re.search(r"(class|struct)\s+(\w+)", line).group(2)
            current_node = {"label": f"Class/Struct ({name})", "children": []}
            nodes.append(current_node)
        
        elif re.match(r"(int|float|double|char)\s+\w+\s*(=.*)?;", line) and current_node:
            var_name = re.search(r"(int|float|double|char)\s+(\w+)", line).group(2)
            current_node["children"].append({"label": f"Variable ({var_name})", "children": []})
        
        elif "return" in line and current_node:
            current_node["children"].append({"label": "Return", "children": []})
    return nodes if nodes else [{"label": "Error: No recognizable C/C++ structure"}]

# Java AST Parsing (using javalang)
def parse_java(code):
    try:
        tree = javalang.parse.parse(code)
        def to_dict(node):
            label = f"{node.__class__.__name__}"
            if hasattr(node, "name"):
                label += f" ({node.name})"
            elif hasattr(node, "value"):
                label += f" ({node.value})"
            children = []
            for attr in node.attrs:
                child = getattr(node, attr)
                if isinstance(child, (list, tuple)):
                    children.extend([to_dict(c) for c in child if c])
                elif child and hasattr(child, "attrs"):
                    children.append(to_dict(child))
            return {"label": label, "children": children}
        return [to_dict(tree)]
    except Exception as e:
        return [{"label": f"Error: {str(e)}"}]
    
# JavaScript AST Parsing (using esprima)
def parse_js(code):
    try:
        tree = esprima.parseScript(code)
        def to_dict(node):
            label = node.type
            if hasattr(node, "name"):
                label += f" ({node.name})"
            elif hasattr(node, "value"):
                label += f" ({node.value})"
            children = []
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    children.extend([to_dict(c) for c in value if hasattr(c, "type")])
                elif hasattr(value, "type"):
                    children.append(to_dict(value))
            return {"label": label, "children": children}
        return [to_dict(tree)]
    except Exception as e:
        return [{"label": f"Error: {str(e)}"}]
    
# Parse Python code into a normalized AST structure.
def parse_python(code):
    tree = ast.parse(code)
    def to_dict(node):
        return {
            "label": node_label(node),
            "children": [to_dict(child) for child in ast.iter_child_nodes(node)]
        }
    return [to_dict(tree)]

# Generic tree builder for normalized AST nodes.
def build_tree(nodes, prefix = "", is_last = True):
    tree_str = []
    for i, node in enumerate(nodes):
        is_last_node = (i == len(nodes) - 1)
        connector = "└── " if is_last_node else "├── "
        label = node.get("label", "Unknown")
        tree_str.append(prefix + connector + label)
        
        children = node.get("children", [])
        new_prefix = prefix + ("    " if is_last_node else "│   ")
        if children:
            tree_str.extend(build_tree(children, new_prefix, is_last_node))
    
    return tree_str

# Generate a label for Python AST nodes.
def node_label(node):
    if isinstance(node, ast.Module):
        return "Module"
    elif isinstance(node, ast.FunctionDef):
        return f"FunctionDef ({node.name})"
    elif isinstance(node, ast.ClassDef):
        return f"ClassDef ({node.name})"
    elif isinstance(node, ast.Name):
        return f"Name ({node.id})"
    elif isinstance(node, ast.arg):
        return f"arg ({node.arg})"
    elif isinstance(node, ast.Assign):
        return "Assign"
    elif isinstance(node, ast.Call):
        return "Call"
    elif isinstance(node, ast.Constant):
        return f"Constant ({node.value})"
    elif isinstance(node, ast.Return):
        return "Return"
    elif isinstance(node, ast.BinOp):
        return "BinOp"
    elif isinstance(node, ast.Add):
        return "Add"
    return type(node).__name__